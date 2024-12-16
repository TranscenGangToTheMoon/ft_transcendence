import httpx
import pyperclip

from utils.credentials import new_user
from utils.request import make_request


def notification(user_to, message):
    return make_request(
        endpoint='notification/',
        method='POST',
        data={'user_to': user_to['id'], 'message': message},
        port=8005,
        token=user_to['token'],
    )


def connect_to_sse(user=None):
    sse_url = "https://localhost:4443/sse/users/"
    print('start sse on', sse_url)
    if user is None:
        user = new_user()

    with httpx.Client(verify=False) as client:
        with client.stream("GET", sse_url, headers={'Authorization': f'Bearer {user["token"]}'}) as response:
            if response.status_code == 200:
                print("Connected to SSE server.")
                for line in response.iter_text():
                    if line.strip():
                        print(f"Received: {line.strip()}")
            else:
                print(f"Failed to connect: {response.status_code}")


if __name__ == "__main__":
    user1 = new_user()

    print(user1['username'], user1['password'])
    pyperclip.copy(user1['username'] + ' ' + user1['password'])
    connect_to_sse(user1)
