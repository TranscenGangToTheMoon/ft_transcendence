from credentials import get_token
import requests

token = get_token()['token']

r = requests.get('http://localhost:8005/api/users/me/', headers={
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
})

print(r.status_code)
print(r.json())
