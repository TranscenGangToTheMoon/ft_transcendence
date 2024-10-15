import json
from pyperclip import copy, paste
import requests

from test_api.credentials import login, register


token = input('whats token type -> ')
if token == 'login':
    token = login()['access']
    copy(token)
elif token == 'register':
    token = register()['access']
    copy(token)
elif token == 'paste':
    token = paste()
else:
    token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzI4OTYwNDU0LCJpYXQiOjE3Mjg5NTY4NTQsImp0aSI6IjJmMTI0MTc0OTBjYzQxZWZhY2RiODEyMTA3MjA4MjlhIiwidXNlcl9pZCI6MTV9.B0jbbTDRbUr3Bn3GCZFyi21mL4mxcuZzurL9yCPihoI'


print(requests.post('http://localhost:8005/api/users/me/friend_requests/', headers={
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
},
                 data=json.dumps({'username': 'coucou'})).json())

print(requests.post('http://localhost:8005/api/users/me/friends/', headers={
    'Authorization': 'Bearer ' + login()['access'],
    'Content-Type': 'application/json'
},
                  data=json.dumps({'username': 'root'})))

r = requests.get('http://localhost:8005/api/users/32/', headers={
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
},
                  data=json.dumps({'username': 'coucou'}))

print(r.status_code)
if r.status_code == 204:
    exit()
print('{')
for k, v in r.json().items():
    if type(k) is str:
        k = '"' + str(k) + '"'
    if type(v) is str:
        v = '"' + v + '"'
    print('\t' + k + ':', str(v) + ',')
print('}')
