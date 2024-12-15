from django.urls import path
from lib_transcendence.endpoints import Users, UsersManagement

from blocking.views import blocked_view, delete_blocked_view
from friend_requests.views import friend_requests_list_create_view, friend_request_view, \
    friend_requests_receive_list_view
from friends.views import friends_view, friend_view
from sse.views import sse_view, notification_view, event_view
from users.views import users_me_view, retrieve_user_view, manage_user_view
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

    path(Users.sse, sse_view),
    path(Users.notification, notification_view),
    path(Users.event, event_view),

    path(Users.chat, validate_chat_view),
    path(Users.are_blocked, are_blocked_view),

    path(UsersManagement.manage_user, manage_user_view),
]

# todo 1 truc jules
# todo 2 truc basile (endpoint)
# todo 2 truc basile finish game

# todo 1. make sse
# todo 7. message discord
# todo 7. message private discord
# todo 2. update user status (connected, disconnected, ...)
# todo 3. if disconnected, send to matchmaking (to leave lobby, tournament, ...)
# todo 4. create endpoint for send notification (message, demande d'amis, demande de join lobby,, demande de join tournament, ...)
# todo 5. create endpoint for send lobby status
# todo 6. create endpoint for send tournament status
# todo 9 send chat_id in lobby or tournament
# todo 10 make dl all data
# todo handle nb spectactgame

# todo game -> {type: game, 'code')
# todo event -> FINISH GAME (args, abandon)
# todo chat -> {type: notification, 'message'}
# todo lobby -> {type: event, 'tournoi', 'id', 'status'}
# todo lobby -> connect chat
# todo tournoi -> connect chat
# todo dans user serializer nb message 1 message, 1 notif dans friend
# todo demande de game only if connected
# todo normaliser les vecteurs
# todo Use verify since me

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

# todo make endpoint for online status
# todo fix github issue
# todo create chat when lobby or tournament is created
# todo delete chat after finish tournament
# todo delete chat after finish lobby

# todo handle local user

# custom game
# - bo et 1v1 | 3v3 (rien a changer)

# - Tournoi pas de seeding

# - get message, mark as read
# - faire inbox notif
# - stocker tous le temps passe sur le site (when SSE)

# - ajouter password field pour change password

# --- before push ---
# todo type all python code (make variable)
# todo check norm
# todo check problem
