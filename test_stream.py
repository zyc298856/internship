import requests

# We first login to get token
resp = requests.post("http://localhost:8000/auth/token", data={"username": "testuser", "password": "testpass"})
token = resp.json().get("access_token")

# Create a session
headers = {"Authorization": f"Bearer {token}"}
resp = requests.post("http://localhost:8000/chat/sessions", data={"title": "Test 1"}, headers=headers)
session_id = resp.json().get("id")

print("Created session:", session_id)

# Post a message
with requests.post(f"http://localhost:8000/chat/sessions/{session_id}/message", data={"text": "Hello, how are you?"}, headers=headers, stream=True) as r:
    for chunk in r.iter_content(chunk_size=None):
        print(repr(chunk.decode("utf-8")))
