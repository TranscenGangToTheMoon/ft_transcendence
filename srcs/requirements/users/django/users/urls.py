from django.urls import path
from lib_transcendence.endpoints import Users

from blocking.views import blocked_list_create_view, blocked_delete_view
from friend_requests.views import friend_requests_list_create_view, friend_requests_delete_view, \
    friend_requests_receive_list_view
from friends.views import friends_list_create_view, friends_delete_view
from users.views import users_me_view, user_retrieve_view
from validate.views import validate_chat_view, are_blocked_view

urlpatterns = [
    path(Users.me, users_me_view),
    path(Users.user, user_retrieve_view),

    path(Users.friends, friends_list_create_view),
    path(Users.friend, friends_delete_view),
    path(Users.friend_requests, friend_requests_list_create_view),
    path(Users.friend_request, friend_requests_delete_view),
    path(Users.friend_requests_receive, friend_requests_receive_list_view),

    path(Users.blocked, blocked_list_create_view),
    path(Users.blocked_user, blocked_delete_view),

    path(Users.chat, validate_chat_view),
    path(Users.are_blocked, are_blocked_view),
]
