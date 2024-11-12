from utils.request import make_request


def send_friend_request(sender, receiver):
    return make_request(
        endpoint='users/me/friend_requests/',
        method='POST',
        token=sender['token'],
        data={'username': receiver['username']}
    )


def accept_friend_request(receiver, sender):
    return make_request(
        endpoint='users/me/friends/',
        method='POST',
        token=receiver['token'],
        data={'username': sender['username']}
    )


def create_friend(user1, user2):
    response_request = send_friend_request(user1, user2)
    response_accept = accept_friend_request(user2, user1)
    return [response_request, response_accept]
