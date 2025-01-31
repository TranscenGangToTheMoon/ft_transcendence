class Auth:
    guest = 'api/auth/guest/'
    register = 'api/auth/register/'
    register_guest = 'api/auth/register/guest/'
    login = 'api/auth/login/'
    refresh = 'api/auth/refresh/'

    verify = 'api/private/auth/verify/'
    update = 'api/private/auth/update/'
    delete = 'api/private/auth/delete/'


class Chat:
    chats = 'api/chat/'
    fchat = 'api/chat/{chat_id}/'
    chat = 'api/chat/<int:chat_id>/'
    fmessages = 'api/chat/{chat_id}/messages/'
    messages = 'api/chat/<int:chat_id>/messages/'
    fmessage = 'api/private/chat/{chat_id}/messages/'
    message = 'api/private/chat/<int:chat_id>/messages/'

    fnotifications = 'api/private/chat/notifications/{user_id}/'
    notifications = 'api/private/chat/notifications/<int:user_id>/'


class Game:
    create_match = 'api/private/match/create/'
    create_match_not_played = 'api/private/match/create/not-played/'
    ffinish_match = 'api/private/match/finish/{match_id}/'
    finish_match = 'api/private/match/finish/<int:match_id>/'
    fscore = 'api/private/match/score/{user_id}/'
    score = 'api/private/match/score/<int:user_id>/'
    fuser = 'api/private/match/{user_id}/'
    user = 'api/private/match/<int:user_id>/'
    fmatch_user = 'api/private/match/{match_id}/{user_id}/'
    match_user = 'api/private/match/<int:match_id>/<int:user_id>/'

    tournaments = 'api/private/tournaments/'

    matches_user = 'api/game/matches/<int:user_id>/'
    tournament = 'api/game/tournaments/<int:tournament_id>/'


class Matchmaking:
    duel = 'api/play/duel/'
    ranked = 'api/play/ranked/'

    lobby = 'api/play/lobby/'
    lobby_participant = 'api/play/lobby/<str:code>/'
    lobby_invite = 'api/play/lobby/<str:code>/invite/<int:user_id>/'
    lobby_ban = 'api/play/lobby/<str:code>/ban/<int:user_id>/'
    lobby_message = 'api/play/lobby/<str:code>/message/'

    tournament = 'api/play/tournament/'
    tournament_search = 'api/play/tournament/search/'
    tournament_participant = 'api/play/tournament/<str:code>/'
    tournament_invite = 'api/play/tournament/<str:code>/invite/<int:user_id>/'
    tournament_ban = 'api/play/tournament/<str:code>/ban/<int:user_id>/'
    tournament_message = 'api/play/tournament/<str:code>/message/'

    lobby_finish_match = 'api/private/lobby/finish-match/'


class Users:
    users = 'api/private/users/'
    me = 'api/users/me/'
    user = 'api/users/<int:user_id>/'

    friends = 'api/users/me/friends/'
    friend = 'api/users/me/friends/<int:friendship_id>/'
    friend_requests = 'api/users/me/friend_requests/'
    ffriend_request = 'api/users/me/friend_requests/{id}/'
    friend_request = 'api/users/me/friend_requests/<int:friend_request_id>/'
    friend_requests_received = 'api/users/me/friend_requests/received/'

    blocked = 'api/users/me/blocked/'
    blocked_user = 'api/users/me/blocked/<int:blocking_id>/'

    stats = 'api/users/me/stats/'
    stats_ranked = 'api/users/me/stats/ranked/'
    result_match = 'api/private/users/result-match/'
    result_tournament = 'api/private/users/result-tournament/'

    profile_pictures = 'api/users/profile-pictures/'
    fprofile_picture = 'api/users/profile-picture/{id}/'
    profile_picture = 'api/users/profile-picture/<int:id>/'

    export_data = 'api/users/me/download-data/'

    sse = 'sse/users/'
    event = 'api/private/users/events/'

    fchat = 'api/private/users/chat/{user1_id}/{username2}/'
    chat = 'api/private/users/chat/<int:user1_id>/<str:username2>/'
    fare_friends = 'api/private/users/friends/{user1_id}/{user2_id}/'
    are_friends = 'api/private/users/friends/<int:user1_id>/<int:user2_id>/'
    auth_matchmaking = 'api/private/users/me/auth-matchmaking/'


class UsersManagement:
    manage_user = 'api/private/user/manage/'
    fexport_data = 'api/private/export-data/{user_id}/'
    export_data = 'api/private/export-data/<int:user_id>/'
    frename_user = 'api/private/user/rename/{user_id}/'
    rename_user = 'api/private/user/rename/<int:user_id>/'
    fblocked_user = 'api/private/user/blocked/{user_id}/{blocked_user_id}/'
    blocked_user = 'api/private/user/blocked/<int:user_id>/<int:blocked_user_id>/'
    fdelete_user = 'api/private/user/delete/{user_id}/'
    delete_user = 'api/private/user/delete/<int:user_id>/'
