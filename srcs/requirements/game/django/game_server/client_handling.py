import json
import uuid
from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class GameClient(WebsocketConsumer):
	def connect(self):
		self.player_id = str(uuid.uuid4())
		self.accept()
		self.send(text_data=json.dumps({
			'type': 'playerid',
			'playerid': self.player_id
		}))

	def disconnect(self, code = None):
		self.send(text_data=json.dumps({
			'type': 'disconnect',
			'message': 'Disconnected from the game server.'
		}))



	def receive(self, text_data = None, bytes_data = None):
		if text_data is not None:
			text_data_json = json.loads(text_data)
			if (text_data_json['type'] == 'username')
			user_name = text_data_json['username']
