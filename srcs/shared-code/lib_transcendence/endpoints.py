base_api = 'api/'


class Auth:
    base_auth = base_api + 'auth/'

    guest = base_auth + 'guest/'
    register = base_auth + 'register/'
    login = base_auth + 'login/'
    refresh = base_auth + 'refresh/'

    verify = base_api + 'verify/'
    update = base_api + 'update/'
    delete = base_api + 'delete/'


class Chat:
    _base_chat = base_api + 'chat/'

    _chat_id = '<int:chat_id>/'
    _fchat_id = '{chat_id}/'
    chats = _base_chat
    chat = chats + _chat_id
    fmessages = chats + _fchat_id + 'messages/'
    messages = fmessages.format(chat_id='<int:chat_id>')


class Game:
    base_game = base_api + 'game/'

    match = base_api + 'match/'
    fmatch_user = match + '{user_id}/'
    match_user = fmatch_user.format(user_id='<int:user_id>')
    tournaments = base_api + 'tournaments/'

    matches_user = base_game + 'matches/<int:user_id>/'
    tournament = base_game + 'tournaments/<int:tournament_id>/'


class Matchmaking:
    base_matchmaking = base_api + 'play/'

    duel = base_matchmaking + 'duel/'
    ranked = base_matchmaking + 'ranked/'

    lobby = base_matchmaking + 'lobby/'
    lobby_participant = lobby + '<str:code>/'
    lobby_kick = lobby_participant + 'kick/<int:user_id>/'

    tournament = base_matchmaking + 'tournament/'
    tournament_search = tournament + 'search/'
    tournament_participant = tournament + '<str:code>/'
    tournament_kick = tournament + '<str:code>/kick/<int:user_id>/'

    tournament_result_match = base_api + 'tournament/result-match/'


class Users:
    base_users = base_api + 'users/'

    me = base_users + 'me/'
    user = base_users + '<int:user_id>/'

    friends = me + 'friends/'
    friend = friends + '<int:friendship_id>/'
    friend_requests = me + 'friend_requests/'
    friend_request = friend_requests + '<int:friend_request_id>/'
    friend_requests_received = friend_requests + 'received/'

    blocked = me + 'blocked/'
    blocked_user = blocked + '<int:blocking_id>/'

    fchat = base_api + 'chat/{user1_id}/{username2}/'
    chat = fchat.format(user1_id='<int:user1_id>', username2='<str:username2>')
    fare_blocked = base_api + 'blocked/{user1_id}/{user2_id}/'
    are_blocked = fare_blocked.format(user1_id='<int:user1_id>', user2_id='<int:user2_id>')


class UsersManagement:
    rename_user = base_api + 'rename-user/<int:user_id>/'
    fblocked_user = base_api + 'blocked-user/{user_id}/{blocked_user_id}/'
    blocked_user = fblocked_user.format(user_id='<int:user_id>', blocked_user_id='<int:blocked_user_id>')
    delete_user = base_api + 'delete-user/<int:user_id>/'


#todo check all internal request urls
#todo raname all _view
#todo in litteral use urls
