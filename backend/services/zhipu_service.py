import os
import json
from zhipuai import ZhipuAI

client = ZhipuAI(api_key=os.environ.get("ZHIPUAI_API_KEY", "your-api-key-here"))

def generate_glm4v_response_stream(messages_history):
    """
    Calls ZhipuAI GLM-4V API with streaming.
    messages_history is parsed from frontend into ZhipuAI format:
    [
        {"role": "user", "content": [{"type": "text", "text": "What is this?"}, {"type": "image_url", "image_url": {"url": "..."}}]},
        {"role": "assistant", "content": [{"type": "text", "text": "This is..."}]}
    ]
    """
    try:
        response = client.chat.completions.create(
            model="glm-4v-plus", # Zhipu's latest multimodal endpoint
            messages=messages_history,
            stream=True
        )
        
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                text_chunk = chunk.choices[0].delta.content
                yield f"data: {json.dumps({'text': text_chunk})}\n\n"
        
        yield "data: [DONE]\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"
        yield "data: [DONE]\n\n"
