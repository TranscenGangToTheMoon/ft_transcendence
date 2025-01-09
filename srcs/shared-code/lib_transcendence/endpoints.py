base_api = 'api/'
base_private_api = base_api + 'private/'
base_sse = 'sse/'
_user_id = '<int:user_id>'


# todo remake all
class Auth:
    _base_auth = base_api + 'auth/'
    _base_private_auth = base_private_api + 'auth/'

    guest = _base_auth + 'guest/'
    register = _base_auth + 'register/'
    register_guest = register + 'guest/'
    login = _base_auth + 'login/'
    refresh = _base_auth + 'refresh/'

    verify = _base_private_auth + 'verify/'
    update = _base_private_auth + 'update/'
    delete = _base_private_auth + 'delete/'


class Chat:
    _base_chat = base_api + 'chat/'
    _base_private_chat = base_private_api + 'chat/'
    _chat_id = '<int:chat_id>'
    _fchat_id_message = '{chat_id}/messages/'

    chats = _base_chat
    fchat = chats + '{chat_id}/'
    chat = fchat.format(chat_id=_chat_id)
    fmessages = chats + _fchat_id_message
    messages = fmessages.format(chat_id=_chat_id)
    fmessage = _base_private_chat + _fchat_id_message
    message = fmessage.format(chat_id=_chat_id)

    fnotifications = _base_private_chat + 'notifications/{user_id}/'
    notifications = fnotifications.format(user_id=_user_id)


class Game:
    _base_game = base_api + 'game/'
    _base_private_game = base_private_api + 'game/'

    _match = _base_private_game + 'match/'
    create_match = _match + 'create/'
    ffinish_match = _match + 'finish/{match_id}/'
    finish_match = ffinish_match.format(match_id="<int:match_id>")
    fscore = _match + 'score/{user_id}/'
    score = fscore.format(user_id=_user_id)
    fmatch_user = _match + '{user_id}/'
    match_user = fmatch_user.format(user_id=_user_id)

    tournaments = _base_private_game + 'tournaments/'

    matches_user = _base_game + f'matches/{_user_id}/'
    tournament = _base_game + 'tournaments/<int:tournament_id>/'


class Matchmaking:
    _base_matchmaking = base_api + 'play/'

    duel = _base_matchmaking + 'duel/'
    ranked = _base_matchmaking + 'ranked/'

    lobby = _base_matchmaking + 'lobby/'
    lobby_participant = lobby + '<str:code>/'
    lobby_invite = lobby_participant + f'invite/{_user_id}/'
    lobby_ban = lobby_participant + f'ban/{_user_id}/'

    tournament = _base_matchmaking + 'tournament/'
    tournament_search = tournament + 'search/'
    tournament_participant = tournament + '<str:code>/'
    tournament_invite = tournament_participant + f'invite/{_user_id}/'
    tournament_ban = tournament_participant + f'ban/{_user_id}/'

    ftournament_result_match = base_private_api + 'tournament/result-match/{match_id}/'
    tournament_result_match = ftournament_result_match.format(match_id='<int:match_id>')


class Users:
    _base_users = base_api + 'users/'
    _base_private_users = base_private_api + 'users/'

    users = _base_private_users
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
    event = _base_private_users + 'events/'

    fchat = _base_private_users + 'chat/{user1_id}/{username2}/'
    chat = fchat.format(user1_id='<int:user1_id>', username2='<str:username2>')
    fare_friends = _base_private_users + 'friends/{user1_id}/{user2_id}/'
    are_friends = fare_friends.format(user1_id='<int:user1_id>', user2_id='<int:user2_id>')


class UsersManagement:
    _base_private_users_management = base_private_api + 'user/'

    manage_user = _base_private_users_management + 'manage/'
    frename_user = _base_private_users_management + 'rename/{user_id}/'
    rename_user = frename_user.format(user_id=_user_id)
    fblocked_user = _base_private_users_management + 'blocked/{user_id}/{blocked_user_id}/'
    blocked_user = fblocked_user.format(user_id=_user_id, blocked_user_id='<int:blocked_user_id>')
    fdelete_user = _base_private_users_management + 'delete/{user_id}/'
    delete_user = fdelete_user.format(user_id=_user_id)
