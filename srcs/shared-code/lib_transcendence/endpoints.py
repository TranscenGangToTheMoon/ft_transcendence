base_api = 'api/'
base_sse = 'sse/'
_user_id = '<int:user_id>'


class Auth:
    _base_auth = base_api + 'auth/'

    guest = _base_auth + 'guest/'
    register = _base_auth + 'register/'
    register_guest = register + 'guest/'
    login = _base_auth + 'login/'
    refresh = _base_auth + 'refresh/'

    verify = base_api + 'verify/'
    update = base_api + 'update/'
    delete = base_api + 'delete/'


class Chat:
    _base_chat = base_api + 'chat/'
    _chat_id = '<int:chat_id>'
    _fchat_id_message = '{chat_id}/messages/'

    chats = _base_chat
    chat = chats + _chat_id + '/'
    fmessages = chats + _fchat_id_message
    messages = fmessages.format(chat_id=_chat_id)
    fmessage = base_api + _fchat_id_message
    message = fmessage.format(chat_id=_chat_id)


class Game:
    _base_game = base_api + 'game/'

    match = base_api + 'match/'
    fmatch_user = match + '{user_id}/'
    match_user = fmatch_user.format(user_id=_user_id)
    tournaments = base_api + 'tournaments/'

    matches_user = _base_game + f'matches/{_user_id}/'
    tournament = _base_game + 'tournaments/<int:tournament_id>/'


class Matchmaking:
    _base_matchmaking = base_api + 'play/'

    duel = _base_matchmaking + 'duel/'
    ranked = _base_matchmaking + 'ranked/'

    lobby = _base_matchmaking + 'lobby/'
    lobby_participant = lobby + '<str:code>/'
    lobby_kick = lobby_participant + f'kick/{_user_id}/'

    tournament = _base_matchmaking + 'tournament/'
    tournament_search = tournament + 'search/'
    tournament_participant = tournament + '<str:code>/'
    tournament_kick = tournament + f'<str:code>/kick/{_user_id}/'

    tournament_result_match = base_api + 'tournament/result-match/'


class Users:
    _base_users = base_api + 'users/'

    me = _base_users + 'me/'
    user = _base_users + f'{_user_id}/'

    friends = me + 'friends/'
    friend = friends + '<int:friendship_id>/'
    friend_requests = me + 'friend_requests/'
    friend_request = friend_requests + '<int:friend_request_id>/'
    friend_requests_received = friend_requests + 'received/'

    blocked = me + 'blocked/'
    blocked_user = blocked + '<int:blocking_id>/'

    sse = base_sse + 'users/'
    notification = base_api + 'notification/'
    event = base_api + 'event/'

    fchat = base_api + 'chat/{user1_id}/{username2}/'
    chat = fchat.format(user1_id='<int:user1_id>', username2='<str:username2>')
    fare_blocked = base_api + 'blocked/{user1_id}/{user2_id}/'
    are_blocked = fare_blocked.format(user1_id='<int:user1_id>', user2_id='<int:user2_id>')


class UsersManagement:
    manage_user = base_api + 'manage-user/'
    frename_user = base_api + 'rename-user/{user_id}/'
    rename_user = frename_user.format(user_id=_user_id)
    fblocked_user = base_api + 'blocked-user/{user_id}/{blocked_user_id}/'
    blocked_user = fblocked_user.format(user_id=_user_id, blocked_user_id='<int:blocked_user_id>')
    fdelete_user = base_api + 'delete-user/{user_id}/'
    delete_user = fdelete_user.format(user_id=_user_id)
