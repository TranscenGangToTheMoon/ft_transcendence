import requests

print(requests.get("http://127.0.0.1:8000/api?product_id=234").text)
