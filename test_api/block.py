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
else:#if token == 'token':
    token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzI4OTAyNTAwLCJpYXQiOjE3Mjg4OTg5MDAsImp0aSI6ImI4ZTMzNDFlMDA1MjRhNDlhZjFkMjVhMTEyZGQzNDZkIiwidXNlcl9pZCI6MTV9.GXZ47XD7jgHpTgIv2JMEpqdvPu_EsZ5VfRF7hexU0-U'
# else:
#     token = paste()
# copy(token)


r = requests.get('http://localhost:8005/api/users/me/block/', headers={
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
},
                 data=json.dumps({'username': 'pipi'}))

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
