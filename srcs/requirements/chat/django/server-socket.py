
import os
import sys
import django
import socketio
import asyncio
from asgiref.sync import async_to_sync, sync_to_async
from aiohttp import web
from lib_transcendence.endpoints import Chat
from lib_transcendence.auth import auth_verify
from lib_transcendence.services import request_chat
from socketio.exceptions import ConnectionRefusedError

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat.settings')

django.setup()

from chats.models import Chats, ChatParticipants

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
        await sio.emit('debug', {'token': token, 'chat_id': chatId}, to=sid)
        try:
            print(f"Trying to authentificate : {sid}")
            res = auth_verify(token)
            await sio.emit('debug', res, to=sid)
            print(f"Connection successeeded {sid}")
        except Exception as e:
            print(f"Authentification failed : {sid}")
            raise ConnectionRefusedError({"error": 401, "message": "Invalid token"})
        await sio.enter_room(sid, str(chatId))
        try:
            usersConnected[sid] = await sync_to_async(ChatParticipants.objects.get, thread_sensitive=False)(user_id=str(res['id']))
        except ChatParticipants.DoesNotExist:
            print(f"Get chatParticipant failed : {sid}")
    else:
        print(f"Connection failed : {sid}")
        raise ConnectionRefusedError({"error": 400, "message": "Missing args"})
    await sio.emit('message', {'author':'', 'content': 'You\'re now connected'}, to=sid)



@sio.event
async def disconnect(sid):
    # usersConnected.pop(sid, None)
    print(f"Client disconnected : {sid}")

@sio.event
async def message(sid, data):
    chatId = data.get('chatId')
    content = data.get('content')
    if (content is None or chatId is None):
        await sio.emit('error', {'error': 400, 'message': 'Invalid message format'}, to=sid)
        await sio.disconnect(sid)
        return
    try:
        await sio.emit('debug', {'chat_id': chatId, 'content': content, 'endpoint': Chat.fmessages.format(chat_id=chatId)}, to=sid)
        request_chat(Chat.fmessages.format(chat_id=chatId), 'POST', {'content': content})
    except Exception as e:
        print(e)
        await sio.emit('error', {'error': 401, 'message': 'Internal server error'}, to=sid)
    print(f"New message from {sid}: {data}")
    await sio.emit('message', {'chatId':chatId, 'author':usersConnected[sid].username, 'content': content}, room=str(chatId))


if __name__ == '__main__':
    web.run_app(app, port=8010)