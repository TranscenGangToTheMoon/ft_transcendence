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
    token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzI5MDM0MjgxLCJpYXQiOjE3MjkwMzA2ODEsImp0aSI6ImExYTY2YzZmZThiMDQ1ODNiMmNhMTk2ZmU3Yjg1MTU5IiwidXNlcl9pZCI6M30._1w_V6qrZZxXr71Im94p4N1QM_0EUG3-6hkDkKe6VEE'


caca_token ='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzI5MDM0NDM2LCJpYXQiOjE3MjkwMzA4MzYsImp0aSI6ImJhZmMzMTUwYTIxNjRkNGM4OGQ3NGY4NDJkNzkxYTQzIiwidXNlcl9pZCI6Mn0.fBTi2HGLpwUezhKXanNC_Xce3FpE1OjJrAJcwthi844'
hey_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzI5MDM0MjgxLCJpYXQiOjE3MjkwMzA2ODEsImp0aSI6ImExYTY2YzZmZThiMDQ1ODNiMmNhMTk2ZmU3Yjg1MTU5IiwidXNlcl9pZCI6M30._1w_V6qrZZxXr71Im94p4N1QM_0EUG3-6hkDkKe6VEE'


r = requests.post('http://localhost:8005/api/users/me/friend_requests/', headers={
    'Authorization': 'Bearer ' + hey_token,
    'Content-Type': 'application/json'
}, data=json.dumps({'username': 'caca'}))

print(r.status_code)
print(r.json())

r = requests.post('http://localhost:8005/api/users/me/friends/', headers={
    'Authorization': 'Bearer ' + caca_token,
    'Content-Type': 'application/json'
}, data=json.dumps({'username': 'hey'}))

print(r.json())

r = requests.get('http://localhost:8005/api/users/validate/chat/', headers={
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
}, data=json.dumps({'username': 'caca'}))

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
