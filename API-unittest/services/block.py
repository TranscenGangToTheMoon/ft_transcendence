from utils.request import make_request


def block_user(user, username):
    return make_request(
        endpoint='users/me/block/',
        method='POST',
        data={'username': username},
        token=user['token'],
    )
