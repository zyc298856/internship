import os
os.environ["DASHSCOPE_API_KEY"] = "265af2319b8b4d1aa56c29216d4c0874.2LsUTDfa4ytM9e6c"

from services.qwen_service import generate_qwen_vl_response_stream

messages_history = [
    {"role": "user", "content": [{"text": "你好"}]}
]

for chunk in generate_qwen_vl_response_stream(messages_history):
    print("CHUNK:", repr(chunk))
