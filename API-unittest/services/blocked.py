from utils.request import make_request


def blocked_user(user, user_id):
    return make_request(
        endpoint='users/me/blocked/',
        method='POST',
        data={'user_id': user_id},
        token=user['token'],
    )


def unblocked_user(user, block_id):
    return make_request(
        endpoint=f'users/me/blocked/{block_id}/',
        method='DELETE',
        token=user['token'],
    )


def are_blocked(user1_id, user2_id):
    return make_request(
        endpoint=f'blocked/{user1_id}/{user2_id}/',
        port=8005,
    )

