from getpass import getpass

import requests

password = getpass()
auth_response = requests.post("http://127.0.0.1:8000/api/auth/", json={"username": "fguirama", "password": password})

print(auth_response.json())

print(requests.post("http://127.0.0.1:8000/api/v2/users-abc/", headers={"Authorization": "Bearer " + auth_response.json()['token']}).json())

exit()

if auth_response.status_code == 200:
    data = {"username": "courgrgcoulekip", 'password': 'blanlablo', "trophy": 3443}

    # create = requests.post("http://127.0.0.1:8000/api/users/", headers={"Authorization": "Token " + auth_response.json()['token']}).json()
    # print(create)
    print(requests.get("http://127.0.0.1:8000/api/users/9/", headers={"Authorization": "Bearer " + auth_response.json()['token']}).json())
    # print(requests.get(f"http://127.0.0.1:8000/api/users/{create['id']}/").json())
    # print(requests.put(f"http://127.0.0.1:8000/api/users/{create['id']}/", json=data).json())
