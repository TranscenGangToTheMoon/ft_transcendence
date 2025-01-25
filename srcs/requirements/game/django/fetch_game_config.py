import json

from lib_transcendence.request import request_service


response = request_service('localhost', 'gameConfig.json', 'GET', port=4443)
assert response is not None

with open('gameConfig.json', 'w', encoding='utf-8') as f:
    json.dump(response, f)
