from utils.request import make_request


def finish_match_stat(data=None):
    if data is None:
        data = {}
    return make_request(
        endpoint='private/users/result-match/',
        port=8005,
        method='POST',
        data=data,
    )

# todo rename all serializer.py -> serializers.py
def get_stats(user):
    return make_request(
        endpoint='users/me/stats/',
        token=user['token'],
    )


def get_ranked_stats(user):
    return make_request(
        endpoint='users/me/stats/ranked',
        token=user['token'],
    )
