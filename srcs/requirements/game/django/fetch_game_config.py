import json

from lib_transcendence.request import request_service


if __name__ == '__main__':
    response = request_service('frontend', 'gameConfig.json', 'GET', port=443)

    with open('gameConfig.json', 'w', encoding='utf-8') as f:
        json.dump(response, f)
        print('save gameConfig.json', flush=True)
