import json

import httpx

from utils.credentials import new_user
from utils.request import make_request
from threading import Thread
from services.sse import events
def connect_to_sse(user=None):
    sse_url = "https://localhost:4443/sse/users/"
    print('start sse on', sse_url)
    if user is None:
        user = new_user()

    with httpx.Client(verify=False, timeout=5000) as client:
        headers = {
            'Authorization': f'Bearer {user["token"]}',
            'Content-Type': 'text/event-stream',
        }
        with client.stream("GET", sse_url, headers=headers) as response:
            if response.status_code == 200:
                print("Connected to SSE server.")
                for line in response.iter_text():
                    if line.strip():
                        print(f"Received: {line.strip()}")
            else:
                print(f"Failed to connect: {response.status_code}")


if __name__ == "__main__":
    user1 = new_user()
    with open('user1.json', 'w') as f:
        json.dump(user1, f, indent=4)
    print(user1['id'], user1['username'], user1['password'])
    Thread(target=events, args=(user1, None, {'message': 'Hello, World!'}, 'chat', 'send-message')).start()
    connect_to_sse(user1)
