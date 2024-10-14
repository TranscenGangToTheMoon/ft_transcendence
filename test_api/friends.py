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
    token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzI4ODk0ODgyLCJpYXQiOjE3Mjg4OTEyODIsImp0aSI6IjU5NWVlMDA5OWFjNjQ4YjVhZGI5MzNiZDk1YzQxNGQ1IiwidXNlcl9pZCI6MzR9.nv1vl5ximFxqpLZ7Emrk4BFTqZHNJtt2IH63i2_hyZE'
# else:
#     token = paste()
# copy(token)


r = requests.post('http://localhost:8005/api/users/me/friend_requests/', headers={
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
},
                  data=json.dumps({'userntame': 'pipi'}))

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
