import json
from channels.generic.websocket import WebsocketConsumer

class customer(WebsocketConsumer):
	def connect(self):
		self.accept()
		self.send(text_data=json.dumps({
			'type': 'connect',
			'message': 'Connected to the matchmaking server.'
		}))

	def disconnect(self, code = None):
		self.send(text_data=json.dumps({
			'type': 'disconnect',
			'message': 'Disconnected from the matchmaking server.'
		}))

	def receive(self, text_data = None, bytes_data = None):
		if text_data is not None:
			text_data_json = json.loads(text_data)
			message = text_data_json['message']
			self.send(text_data=json.dumps({
				'type': 'message',
				'message': message
			}))
