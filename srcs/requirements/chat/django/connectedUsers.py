class ConnectedUsers:
    def __init__(self):
        self.users_sid = {}
        self.users_id = {}

    def add_user(self, id, sid, username, chat_id, chat_type, chat_with_id=None):
        self.users_sid[sid] = {
            'user_id': id,
            'username': username,
            'chat_id': chat_id,
            'chat_type': chat_type,
            'chat_with_id': chat_with_id,
        }
        self.users_id[id] = {
            'sid': sid,
            'chat_id': chat_id,
        }

    def remove_user(self, sid):
        user = self.users_sid.pop(sid, None)
        if user:
            self.users_id.pop(user['user_id'], None)

    def is_user_connected(self, id):
        if self.users_id.get(id):
            return True
        return False

    def get_user_id(self, sid):
        user = self.users_sid.get(sid)
        if user:
            return user['user_id']
        return None
    
    def get_username(self, sid):
        user = self.users_sid.get(sid)
        if user:
            return user['username']
        return None

    def get_chat_with_id(self, sid):
        user = self.users_sid.get(sid)
        if user:
            return user['chat_with_id']
        return None

    def get_user_sid(self, id):
        user = self.users_id.get(id)
        if user:
            return user['sid']
        return None

    def get_chat_id(self, sid):
        user = self.users_sid.get(sid)
        if user:
            return user['chat_id']
        return None

    def is_chat_with_connected_with_him(self, sid):
        user = self.users_sid.get(sid)
        if user and user['chat_with_id']:
            searched_user = self.users_id.get(user['chat_with_id'])
            if searched_user and searched_user['chat_id'] == user['chat_id']:
                return True
        return False
    
    def is_private_chat(self, sid):
        user = self.users_sid.get(sid)
        if user and user['chat_type'] == 'private_message':
            return True
        return False
