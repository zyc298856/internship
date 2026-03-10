import httpx
import json

client = httpx.Client()
resp = client.post("http://localhost:8000/auth/token", data={"username": "testuser", "password": "testpass"})
token = resp.json().get("access_token")

headers = {"Authorization": f"Bearer {token}"}
resp = client.post("http://localhost:8000/chat/sessions", data={"title": "Test 1"}, headers=headers)
session_id = resp.json().get("id")

print("Created session:", session_id)

with client.stream("POST", f"http://localhost:8000/chat/sessions/{session_id}/message", data={"text": "你好"}, headers=headers) as r:
    for chunk in r.iter_bytes(chunk_size=1024):
        print("RAW CHUNK:", chunk)
        print("DECODED:", chunk.decode('utf-8'))
