import json
from typing import Literal

import requests


class RequestResult:
    def __init__(self, status_code, json_data=None):
        self.status_code = status_code
        if json_data is None:
            json_data = {}
        self.json = json_data


def make_request(endpoint, method: Literal['GET', 'POST', 'DELETE', 'PATCH', 'PUT'] = 'GET', token=None, data=None, port=4443):
    if data is not None:
        data = json.dumps(data)

    headers = {
        'Content-Type': 'application/json',
    }
    if token is not None:
        headers['Authorization'] = f'Bearer {token}'

    r = requests.request(
        method=method,
        url=f'http{"s" if port == 4443 else ""}://localhost:{port}/api/{endpoint}',
        headers=headers,
        data=data,
        verify=False,
    )

    if 'auth' not in endpoint:
        print(method, endpoint, '=>', r.status_code)

    if r.status_code == 204:
        return RequestResult(r.status_code)

    try:
        result = r.json()
        if 'auth' in endpoint:
            return result
        else:
            print('JSON =>', result)
        return RequestResult(r.status_code, result)
    except json.decoder.JSONDecodeError:
        pass
