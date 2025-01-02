class ConnectedUsers:
	def __init__(self):
		self.users_sid = {}
		self.users_id = {}

	def add_user(self, id, sid, chat_id, chat_with_id=None):
		self.users_sid[sid] = {
			'user_id': id,
			'chat_id': chat_id,
			'chat_with_id': chat_with_id,
		}
		self.users_id[id] = {
			'chat_id': chat_id,
		}

	def remove_user(self, sid):
		user = self.users_sid.pop(sid, None)
		if user:
			self.users_id.pop(user['user_id'], None)

	def get_chat_id(self, sid):
		user = self.users_sid.get(sid)
		if user:
			return user['chat_id']
		return None

	def is_chat_with_connected_with_him(self, sid):
		user = self.users_sid.get(sid)
		if user and user['chat_with_id']:
			searched_user =  self.users_id.get(user['chat_with_id'])
			if searched_user and searched_user['chat_id'] == user['chat_id']:
				return True
		return False