from utils.request import make_request


def blocked_user(user, username):
    return make_request(
        endpoint='users/me/blocked/',
        method='POST',
        data={'username': username},
        token=user['token'],
    )


def unblocked_user(user, block_id):
    return make_request(
        endpoint=f'users/me/blocked/{block_id}/',
        method='DELETE',
        token=user['token'],
    )
