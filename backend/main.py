from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from database import init_db
from routers import auth, chat

app = FastAPI(title="Qwen-VL Chat API")

# Initialize database
init_db()

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:5173", 
    "http://localhost:8080",
    "http://127.0.0.1:5173",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chat.router)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Qwen-VL Service is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
