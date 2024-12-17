
import os
import sys
import django
import socketio
import asyncio
from asgiref.sync import async_to_sync, sync_to_async
from aiohttp import web
from lib_transcendence.endpoints import Chat
from lib_transcendence.auth import auth_verify
from lib_transcendence.services import post_messages
from lib_transcendence.services import request_chat
from lib_transcendence.request import request_service
from rest_framework.exceptions import AuthenticationFailed
from socketio.exceptions import ConnectionRefusedError

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat.settings')

django.setup()

from chats.models import Chats, ChatParticipants
from chat_messages.models import Messages

sio = socketio.AsyncServer(cors_allowed_origins='*', async_mode='aiohttp', logger=True)
app = web.Application()
sio.attach(app, socketio_path='/ws/chat/')

usersConnected = {}

@sio.event
async def connect(sid, environ):
    print(f"Client attempting to connect : {sid}")
    token = environ.get('HTTP_TOKEN')
    chatId = environ.get('HTTP_CHATID')
    if token and chatId:
        try:
            print(f"Trying to authentificate : {sid}")
            res = auth_verify(token)
            await sio.emit('debug', res, to=sid)
            print(f"Connection successeeded {sid}")
        except AuthenticationFailed:
            print(f"Authentification failed : {sid}")
            raise ConnectionRefusedError({"error": 401, "message": "Invalid token"})
        await sio.enter_room(sid, str(chatId))
        # try:
        #     usersConnected[sid] = await sync_to_async(ChatParticipants.objects.get, thread_sensitive=False)(user_id=str(res['id']), chat_id=str(chatId))
        #     await sio.emit(
        #         'debug',
        #         {'username': usersConnected[sid].username, 'userId':usersConnected[sid].user_id},
        #         to=sid
        #     )
        #     await sio.emit(
        #         'debug',
        #         {'username': usersConnected[sid].chat},
        #         to=sid
        #     )
        # except ChatParticipants.DoesNotExist:
        #     await sio.emit(
        #         'debug',
        #         {'username': 'failed', 'userId': 'failed'},
        #         to=sid
        #     )
        #     print(f"Get chatParticipant failed : {sid}")
    else:
        print(f"Connection failed : {sid}")
        raise ConnectionRefusedError({"error": 400, "message": "Missing args"})
    await sio.emit('message', {'author':'', 'content': 'You\'re now connected'}, to=sid)



@sio.event
async def disconnect(sid):
    usersConnected.pop(sid, None)
    print(f"Client disconnected : {sid}")

@sio.event
async def message(sid, data):
    chatId = data.get('chatId')
    content = data.get('content')
    token = data.get('token')
    print(f"New message from {sid}: {data}")
    if (content is None or chatId is None):
        await sio.emit(
            'error',
            {'error': 400, 'message': 'Invalid message format'},
            to=sid
        )
        await sio.disconnect(sid)
        return
    try:
        await sync_to_async(post_messages, thread_sensitive=False)(chatId, content, token)
        await sio.emit(
            'message',
            {'chatId':chatId, 'author':'temporary no available', 'content': content},
            room=str(chatId)
        )
        print(f"Message saved and sent from {sid}: {data}")
    except Exception as e:
        await sio.emit(
            'error',
            {'error': 400, 'message': 'Invalid token'},
            to=sid
        )
        print(f"Error: {e}")
    except AuthenticationFailed:
        print(f"Authentification failed : {sid}")
        await sio.emit(
            'error',
            {'error': 401, 'message': 'Invalid token'},
            to=sid
        )


if __name__ == '__main__':
    web.run_app(app, port=8010)