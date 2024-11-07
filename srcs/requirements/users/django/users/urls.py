from django.urls import path
from lib_transcendence.endpoints import Users

from block.views import block_list_create_view, block_delete_view
from friend_requests.views import friend_requests_list_create_view, friend_requests_delete_view, \
    friend_requests_receive_list_view
from friends.views import friends_list_create_view, friends_delete_view
from users.views import users_me_view, user_retrieve_view
from validate.views import validate_chat_view, validate_block_view

urlpatterns = [
    path(Users.me, users_me_view),
    path(Users.user, user_retrieve_view),

    path(Users.friends, friends_list_create_view),
    path(Users.friend, friends_delete_view),
    path(Users.friend_requests, friend_requests_list_create_view),
    path(Users.friend_request, friend_requests_delete_view),
    path(Users.friend_requests_receive, friend_requests_receive_list_view),

    path(Users.block, block_list_create_view),
    path(Users.block_user, block_delete_view),

    path(Users.chat, validate_chat_view),
    path(Users.blocked, validate_block_view), # todo rename
]
