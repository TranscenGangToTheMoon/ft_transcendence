
import os
import sys
import django
import socketio
import asyncio
from aiohttp import web
from lib_transcendence.auth import auth_verify

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat.settings')

django.setup()

from chats.models import Chats, ChatParticipants

sio = socketio.AsyncServer(cors_allowed_origins='*', async_mode='aiohttp', logger=True)
app = web.Application()
sio.attach(app, socketio_path='/ws/chat/')

@sio.event
async def connect(sid, environ):
    print(f"Client attempting to connect : {sid}")
    token = environ.get('HTTP_TOKEN')
    chat_id = environ.get('HTTP_CHATID')
    await sio.emit('debug', {'token': token, 'chat_id': chat_id}, to=sid)
    if token and chat_id:
        try:
            print("trying to auth")
            res = auth_verify(token)
            await sio.emit('message', {'message': "<em>Authentification validated!</em>"}, to=sid)
        except Exception as e:
            print("token error")
            await sio.emit('message', {'message': '<em>Invalid token!</em>',}, to=sid)
            # await sio.disconnect(sid)
        print(f"Connection successeeded{sid}")
        try:
            test = Chats.objects.get(id=chat_id)
            print(test)
            await sio.emit('debug', {test}, to=sid)
        except Exception as e:
            print(e)
        await sio.emit('message', {'message': '<em>Welcome!</em>',}, to=sid)
    else:
        print(f"Connection failed{sid}")
        await sio.emit('message', {'message': '<em>missing args!</em>',}, to=sid)
        # await sio.disconnect(sid)


@sio.event
async def disconnect(sid):
    print(f"Client disconnected : {sid}")

@sio.event
async def message(sid, data):
    message = data.get('message')
    print(f"New message from {sid}: {data}")
    await sio.emit('message', {'message': message})


if __name__ == '__main__':
    web.run_app(app, port=8010)