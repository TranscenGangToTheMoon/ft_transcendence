import requests


data = {"username": "courgrgcoulekip", 'password': 'blanlablo', "trophy": 3443}

create = requests.post("http://127.0.0.1:8000/api/users/").json()
print(create)
print(requests.put(f"http://127.0.0.1:8000/api/users/{create['id']}/", json=data).json())
