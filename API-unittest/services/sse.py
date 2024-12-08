from utils.request import make_request


def sse(user):
    make_request('users/me/sse/', token=user['token'])
