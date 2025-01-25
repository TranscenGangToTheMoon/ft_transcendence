import json
import os

import requests

from lib_transcendence.request import request_service

SSL_CRT = 'ft_transcendence.crt'
host = 'localhost'
port = 4443

if __name__ == '__main__':
    print('Fetching game config...', flush=True)
    os.system(f"openssl s_client -connect {host}:{port} -servername {host} </dev/null 2>/dev/null | sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' > {SSL_CRT}")
    url_protocol = 'http'
    service = '127.0.0.1'
    endpoint = 'gameConfig.json'
    headers = {'Content-Type': 'application/json'}
    data = None
    port = 4443
    if port == 4443:
        url_protocol += 's'
    print(f'{url_protocol}://{service}:{port}/{endpoint}', flush=True)
    response = requests.request(
        method='GET',
        url=f'{url_protocol}://{service}:{port}/{endpoint}',
        headers=headers,
        data=data,
        verify=SSL_CRT,
    ).json()
    # response = request_service('localhost', , 'GET', port=4443)
    print('REPSONSE', response, flush=True)
    assert response is not None

    with open('gameConfig.json', 'w', encoding='utf-8') as f:
        print('SATRT WRITE FILE', flush=True)
        json.dump(response, f)
        print('save gameConfig.json', flush=True)
