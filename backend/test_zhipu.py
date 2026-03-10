import os
from zhipuai import ZhipuAI
import json

client = ZhipuAI(api_key=os.environ.get("ZHIPUAI_API_KEY"))

messages = [
    {"role": "user", "content": [{"type": "text", "text": "你好"}]}
]

response = client.chat.completions.create(
    model="glm-4v",
    messages=messages,
    stream=True
)

for chunk in response:
    print(repr(chunk))
