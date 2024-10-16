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
    token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzI5MDk1MDQ1LCJpYXQiOjE3MjkwOTE0NDUsImp0aSI6IjkwYWQ1M2M0MjkzMTQ3YjZhNjRhODA4NTk3ZWNlNDQxIiwidXNlcl9pZCI6MTV9.abfI1MTn5mgij6ldNZ_KTSQNMb2cLsafAAVkZco76go'

# r = requests.get('http://localhost:8005/api/users/validate/chat/', headers={
#     'Authorization': 'Bearer ' + token,
#     'Content-Type': 'application/json'
# }, data=json.dumps({'username': 'caca'}))
# print(r.status_code)
# print(r.json())

r = requests.get('http://localhost:8002/api/chat/10/messages/', headers={
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
}, data=json.dumps({'username': 'caca', 'type': 'private_message', 'content': 'first'}))

print(r.status_code)
if r.status_code == 204 or r.status_code == 500:
    exit()

print('{')
for k, v in r.json().items():
    if type(k) is str:
        k = '"' + str(k) + '"'
    if type(v) is str:
        v = '"' + v + '"'
    print('\t' + k + ':', str(v) + ',')
print('}')
