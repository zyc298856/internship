from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
import shutil

from database import get_db
import models
from routers.auth import get_current_user
from services.zhipu_service import generate_glm4v_response_stream

router = APIRouter(prefix="/chat", tags=["chat"])

UPLOAD_DIR = "/app/uploads"
if not os.path.exists(UPLOAD_DIR):
    # Fallback to local
    UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")
    os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/sessions")
def get_sessions(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    sessions = db.query(models.ChatSession).filter(models.ChatSession.user_id == current_user.id).all()
    return [{"id": s.id, "title": s.title, "created_at": s.created_at} for s in sessions]

@router.post("/sessions")
def create_session(title: str = Form("New Chat"), db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    session = models.ChatSession(user_id=current_user.id, title=title)
    db.add(session)
    db.commit()
    db.refresh(session)
    return {"id": session.id, "title": session.title, "created_at": session.created_at}

@router.delete("/sessions/{session_id}")
def delete_session(session_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id, models.ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    db.query(models.Message).filter(models.Message.session_id == session_id).delete()
    db.delete(session)
    db.commit()
    return {"status": "success"}

@router.get("/sessions/{session_id}/messages")
def get_messages(session_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id, models.ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    messages = session.messages
    return [{"id": m.id, "role": m.role, "type": m.type, "content": m.content, "created_at": m.created_at} for m in messages]

@router.post("/sessions/{session_id}/message")
async def send_message(
    session_id: int,
    text: str = Form(...),
    image: Optional[UploadFile] = File(None),
    image_url: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id, models.ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Process image if uploaded
    saved_url = None
    if image:
        ext = image.filename.split('.')[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        # Note: in a real app, you would serve this file and pass the URL to Qwen, or pass file:// path
        saved_url = f"file://{filepath}"
    elif image_url:
        saved_url = image_url

    # Save user message to DB
    user_content = text
    if saved_url:
        user_content = f"[{saved_url}]\n{text}" # store simple format in db
    
    user_msg = models.Message(session_id=session.id, role="user", type="text", content=user_content)
    db.add(user_msg)
    db.commit()
    
    # Prepare history for GLM-4V
    import base64
    messages_history = []
    # Simplified history processing for multimodal API format
    for m in session.messages:
        if m.role == 'user':
            content_list = []
            m_text = m.content
            has_image = False
            if m_text.startswith('[') and ']\n' in m_text:
                img_path, rest_text = m_text.split(']\n', 1)
                img_path = img_path[1:] # remove [
                
                # ZhipuAI requires base64 for local images or public HTTP URLs
                if img_path.startswith("file://"):
                    local_path = img_path[7:]
                    try:
                        with open(local_path, "rb") as f:
                            encoded_string = base64.b64encode(f.read()).decode("utf-8")
                        # Guess mime type based on extension
                        ext = local_path.split('.')[-1].lower()
                        mime_type = f"image/{ext}" if ext in ['png', 'jpg', 'jpeg', 'webp', 'gif'] else "image/jpeg"
                        img_url = f"data:{mime_type};base64,{encoded_string}"
                    except Exception:
                        img_url = "" # Fallback if file missing
                else:
                    img_url = img_path
                    
                if img_url:
                    content_list.append({"type": "image_url", "image_url": {"url": img_url}})
                
                m_text = rest_text
                has_image = True
                
            if has_image:
                content_list.append({"type": "text", "text": m_text})
                messages_history.append({"role": "user", "content": content_list})
            else:
                messages_history.append({"role": "user", "content": m_text})
        else:
            messages_history.append({"role": "assistant", "content": m.content})
    
    # We need a proxy generator to simultaneously save the assistant's reply to DB when stream ends
    async def event_generator():
        generator = generate_glm4v_response_stream(messages_history)
        final_text = ""
        import asyncio
        import json
        
        for chunk in generator:
            if chunk.startswith("data: {"):
                try:
                    data = json.loads(chunk[6:])
                    if 'text' in data:
                        text_content = data['text']
                        final_text += text_content
                        # Simulate smooth typewriter effect by yielding char by char
                        for char in text_content:
                            char_chunk = f"data: {json.dumps({'text': char})}\n\n"
                            yield char_chunk
                            await asyncio.sleep(0.02) # 20ms delay per character
                        continue # We already yielded this data, skip the pure chunk yield
                except:
                    pass
            yield chunk
            
        # Stream finished, save to DB
        if final_text:
            assistant_msg = models.Message(session_id=session.id, role="assistant", type="text", content=final_text)
            db.add(assistant_msg)
            db.commit()
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")
