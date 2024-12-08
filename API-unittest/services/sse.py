import httpx

from utils.credentials import new_user


def connect_to_sse(user=None):
    sse_url = "https://localhost:4443/api/users/me/sse/"
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
