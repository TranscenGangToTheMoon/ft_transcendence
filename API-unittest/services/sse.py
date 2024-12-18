from utils.request import make_request


def notification(user_to, message):
    return make_request(
        endpoint='private/users/notification/',
        method='POST',
        data={'user_id': user_to['id'], 'message': message},
        port=8005,
        token=user_to['token'],
    )
