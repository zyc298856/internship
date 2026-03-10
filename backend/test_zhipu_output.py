import os
import json
from zhipuai import ZhipuAI

client = ZhipuAI(api_key=os.environ.get("ZHIPUAI_API_KEY"))

messages = [
    {"role": "user", "content": [{"type": "text", "text": "你好"}]}
]

print("Calling Zhipu...")
response = client.chat.completions.create(
    model="glm-4v",
    messages=messages,
    stream=True
)

for chunk in response:
    if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
        val = chunk.choices[0].delta.content
        print(f"CHUNK RAW: {repr(val)}")
        print(f"JSON DUMP: {json.dumps({'text': val})}")
