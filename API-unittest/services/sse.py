from typing_extensions import Literal

from utils.request import make_request


def events(user_to, message, type: Literal['notification'] = 'notification', service: Literal['messages'] = 'messages'):
    return make_request(
        endpoint='private/users/events/',
        method='POST',
        data={'user_id': user_to['id'], 'message': message, 'type': type, 'service': service},
        port=8005,
        token=user_to['token'],
    )
