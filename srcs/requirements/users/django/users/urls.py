from django.urls import path

from blocking.views import blocked_view, delete_blocked_view
from events.views import events_view
from export_data.views import export_data_view
from friend_requests.views import friend_requests_list_create_view, friend_request_view, friend_requests_receive_list_view
from friends.views import friends_view, friend_view
from lib_transcendence.endpoints import Users, UsersManagement
from profile_pictures.views import profile_pictures_view, set_profile_picture_view
from sse.views import sse_view
from stats.views import finish_match_view, stats_view, stats_ranked_view, finish_tournament_view
from users.views import users_me_view, retrieve_user_view, retrieve_users_view, manage_user_view
from validate.views import validate_chat_view, are_friends_view

urlpatterns = [
    path(Users.me, users_me_view),
    path(Users.user, retrieve_user_view),
    path(Users.users, retrieve_users_view),

    path(Users.friend_requests, friend_requests_list_create_view),
    path(Users.friend_request, friend_request_view),
    path(Users.friend_requests_received, friend_requests_receive_list_view),

    path(Users.friends, friends_view),
    path(Users.friend, friend_view),

    path(Users.blocked, blocked_view),
    path(Users.blocked_user, delete_blocked_view),

    path(Users.stats, stats_view),
    path(Users.stats_ranked, stats_ranked_view),
    path(Users.result_match, finish_match_view),
    path(Users.result_tournament, finish_tournament_view),

    path(Users.profile_pictures, profile_pictures_view),
    path(Users.profile_picture, set_profile_picture_view),

    path(Users.export_data, export_data_view),

    path(Users.sse, sse_view),
    path(Users.event, events_view),

    path(Users.chat, validate_chat_view),
    path(Users.are_friends, are_friends_view),

    path(UsersManagement.manage_user, manage_user_view),
]
