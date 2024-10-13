import json
from pyperclip import copy, paste
import requests

from test_api.credentials import login, register

token = input('whats token type -> ')
if token == 'login':
    token = login()['access']
elif token == 'register':
    token = register()['access']
else:
    token = paste()
copy(token)



password = input('delete password -> ')

r = requests.get('http://localhost:8005/api/users/me/', headers={
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
}, data=json.dumps({'password': password}))

print(r.status_code)
print('{')
for k, v in r.json().items():
    if type(k) is str:
        k = '"' + str(k) + '"'
    if type(v) is str:
        v = '"' + v + '"'
    print('\t' + k + ':', str(v) + ',')
print('}')
