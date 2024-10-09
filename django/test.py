import requests

token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzI4NDgzMTU4LCJpYXQiOjE3Mjg0Nzk1NTgsImp0aSI6IjAwNjJiOWYwMDg5MTQ2NmQ5NGMwYmFjYTE5ZTUzNzlmIiwidXNlcl9pZCI6MX0.cED3WDp0jeclI-g-sYXARY7lUROikPmgNl1k1pwuXHg'

r = requests.get('http://127.0.0.1:8000/api/users/send_friend_request/', headers={'Authorization': 'Bearer ' + token, 'content-type': 'application/json'}, json={'q': 'howefher'})
print(r.json())
