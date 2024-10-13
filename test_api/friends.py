import json
from pyperclip import copy, paste
import requests

from test_api.credentials import login, register


token = input('whats token type -> ')
if token == 'login':
    token = login()['access']
elif token == 'register':
    token = register()['access']
elif token == 'token':
    token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzI4Nzg1NTA0LCJpYXQiOjE3Mjg3ODE5MDQsImp0aSI6IjEyOTcwMTNhOTgzNDQ1ZGZiYTg0MWNjODEwMmQwZTE0IiwidXNlcl9pZCI6MzB9.CXDeWocKyLlafFIxWjMp2iFqshKKwqoomjYjx1CpsPg'
    # token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzI4NzgxODc2LCJpYXQiOjE3Mjg3NzgyNzYsImp0aSI6IjA1NGYxOGUzZjQwNTRkNWNiNThlMDYwOWM5OWE2ODAyIiwidXNlcl9pZCI6MTV9.-SUULh3SpIaLXYPxe5VRxIxJc1oWYYCt6Er0vnB1fU4'
    # token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzI4Nzc5NDg1LCJpYXQiOjE3Mjg3NzU4ODUsImp0aSI6IjFjYmUwMmViMGY3YTRmNDlhNzJiN2UwZjMwZDFkMjYwIiwidXNlcl9pZCI6MzB9.KhAVZyOzpEJszXE3xrFW_peC6eqWsm1-xzFeVhyOAEw'
else:
    token = paste()
copy(token)


r = requests.post('http://localhost:8005/api/users/me/friends/', headers={
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
},
                  data=json.dumps({'username': 'coucou'}))

print(r.status_code)
print('{')
for k, v in r.json().items():
    if type(k) is str:
        k = '"' + str(k) + '"'
    if type(v) is str:
        v = '"' + v + '"'
    print('\t' + k + ':', str(v) + ',')
print('}')
