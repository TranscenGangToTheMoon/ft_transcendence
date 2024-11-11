from utils.request import make_request


def blocked_user(user, username):
    return make_request(
        endpoint='users/me/blocked/',
        method='POST',
        data={'username': username},
        token=user['token'],
    )
