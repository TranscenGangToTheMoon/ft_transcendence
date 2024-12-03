from django.urls import path
from lib_transcendence.endpoints import Users

from blocking.views import blocked_view, delete_blocked_view
from friend_requests.views import friend_requests_list_create_view, friend_request_view, \
    friend_requests_receive_list_view
from friends.views import friends_view, friend_view
from users.views import users_me_view, retrieve_user_view
from validate.views import validate_chat_view, are_blocked_view

urlpatterns = [
    path(Users.me, users_me_view),
    path(Users.user, retrieve_user_view),

    path(Users.friend_requests, friend_requests_list_create_view),
    path(Users.friend_request, friend_request_view),
    path(Users.friend_requests_received, friend_requests_receive_list_view),

    path(Users.friends, friends_view),
    path(Users.friend, friend_view),

    path(Users.blocked, blocked_view),
    path(Users.blocked_user, delete_blocked_view),

    path(Users.chat, validate_chat_view),
    path(Users.are_blocked, are_blocked_view),
]

# 1. todo handle delete user
# 2. todo handle rename user
# 3. todo handle create user

# todo make endpoint for user stats, xp, trophies (when match ended, or when tournament ended) WAIT REUNION

# todo make endpoint for online status
# todo fix github issue
# todo create chat when lobby or tournament is created
# todo delete chat after finish tournament
# todo delete chat after finish lobby
# todo make season WAIT REUNION

# --- before push ---
# todo type all python code (make variable)
# todo check norm
# todo check problem
