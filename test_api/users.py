import json

import requests

from test_api.credentials import login

token = login()['access']
# print(token)

r = requests.patch('http://localhost:8005/api/users/me/', headers={
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
}, data=json.dumps({'accept_friend_request': False}))

print(r.status_code)
print('{')
for k, v in r.json().items():
    if type(k) is str:
        k = '"' + str(k) + '"'
    if type(v) is str:
        v = '"' + v + '"'
    print('\t' + k + ':', str(v) + ',')
print('}')
