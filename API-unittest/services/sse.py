from typing_extensions import Literal

from utils.request import make_request


def events(user_to, message, type: Literal['notification'] = 'notification', service: Literal['chat'] = 'chat', event_code: Literal['send-message'] = 'send-message'):
    return make_request(
        endpoint='private/users/events/',
        method='POST',
        data={'users_id': [user_to['id']], 'data': {'message': message}, 'type': type, 'event_code': event_code, 'service': service},
        port=8005,
        token=user_to['token'],
    )
