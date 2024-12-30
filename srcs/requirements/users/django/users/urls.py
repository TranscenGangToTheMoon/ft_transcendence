from django.urls import path
from lib_transcendence.endpoints import Users, UsersManagement

from blocking.views import blocked_view, delete_blocked_view
from friend_requests.views import friend_requests_list_create_view, friend_request_view, \
    friend_requests_receive_list_view
from friends.views import friends_view, friend_view
from events.views import events_view
from sse.views import sse_view
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

    path(Users.sse, sse_view),
    path(Users.event, events_view),

    path(Users.chat, validate_chat_view),
    path(Users.are_friends, are_friends_view),

    path(UsersManagement.manage_user, manage_user_view),
]

# todo 1. fix permision denied guest
# todo 2. test when connected to SSE and rename user and make requestto users service

# todo 1. make sse tournament events

# todo CHAT
#   - create chat when lobby is created
#   - create chat when tournament is created
#   - delete chat when tournament is finish
#   - delete chat when lobby is destroy
#   - send chat_id in lobby
#   - send chat_id in tournament

# todo handle abandon when finish game

# todo game -> {type: game, 'code')
# todo event -> FINISH GAME (args, abandon)
# todo chat -> {type: notification, 'message'}
# todo lobby -> {type: event, 'tournoi', 'id', 'status'}
# todo lobby -> connect chat
# todo tournoi -> connect chat


# todo handle friends fields
# todo make endpoint for user stats, xp, trophies (when match ended, or when tournament ended)
# - pas de stat (custom_game)
# - stat tournoi gagne
# - stat tournoi point marque en tournoi
# - stat tournoi nombre de game gagne
# - stat tournoi nombre de game joue

# - stat ranked evolution du ranked au file du temps
# - stat ranked nb de point
# - stat ranked win
# - stat ranked play

# - stat 1v1 nb de point
# - stat 1v1 win
# - stat 1v1 play

# - stat 3v3 nb de point
# - stat 3v3 win
# - stat 3v3 play
# - stat 3v3 csc

# - stat total partie faite
# - stat total point marque
# - stat total win

# - stat ranked max elo

# - delete season
# - delete coin
# - delete xp


# todo fix github issue
# todo make seeding tournament
# todo ajouter password field pour change password


# ----------------------
# todo handle download all data


# --- poubell a idee ---
# todo handle nb spectact game

# --- before push ---
# todo type all python code (make variable)
# todo check norm (sort line all import)
# todo delete __str__ for all models
# todo check problem
