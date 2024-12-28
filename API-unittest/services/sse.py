from typing_extensions import Literal

from utils.request import make_request
import time

def events(user_to=None, users=None, data=None, service: Literal['chat'] = 'chat', event_code: Literal['send-message'] = 'send-message'):
    time.sleep(1)
    if users is None:
        users = []
    if user_to is not None:
        users.append(user_to['id'])
    else:
        users.append(1)
    return make_request(
        endpoint='private/users/events/',
        method='POST',
        data={'users_id': users, 'data': data, 'event_code': event_code, 'service': service},
        port=8005,
    )
