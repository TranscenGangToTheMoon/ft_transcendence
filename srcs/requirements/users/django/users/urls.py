from django.urls import path
from lib_transcendence.endpoints import Users

from blocking.views import blocked_list_create_view, blocked_delete_view
from friend_requests.views import friend_requests_list_create_view, friend_request_view, \
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
    path(Users.friend_request, friend_request_view),
    path(Users.friend_requests_received, friend_requests_receive_list_view),

    path(Users.blocked, blocked_list_create_view),
    path(Users.blocked_user, blocked_delete_view),

    path(Users.chat, validate_chat_view),
    path(Users.are_blocked, are_blocked_view),
]

# todo handle delete user
# todo handle rename user

# todo make endpoint for user stats
# todo make endpoint for user xp
# todo make endpoint for user trophies
# todo make endpoint for coins
# todo rename all view for more comprehensive name
# todo secure all get_object with filter_queryset
# todo make endpoint for online status
# todo make endpoint for user rank
# todo remake user auth update value (is_guest and username)
# todo make endpoint for match history
 # todo WHEN MAKE DA - make also test at the same time
 # todo test all endpoint
 # todo make doc for all services
 # todo fix github issue
# todo create chat when lobby or tournament is created
# todo delete chat after finish tournament
# todo delete chat after finish lobby
# todo make test for that
# todo make doc for all endpoint
#todo make season
# todo make ranks
#todo make request when a user win a tournament (for coins and xp win)
# todo see new message in chat preview
# todo when guest ca fait longtemps que pas connecter, delete guest (just check si jamais, il est dans un match)