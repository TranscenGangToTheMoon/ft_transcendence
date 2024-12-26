
import os
import sys
import django
import asyncio
import socketio
from aiohttp import web
from asgiref.sync import async_to_sync, sync_to_async
from connectedUsers import ConnectedUsers
from lib_transcendence.auth import auth_verify
from lib_transcendence.services import post_messages
from lib_transcendence.services import request_chat
from lib_transcendence.endpoints import Chat as endpoint_chat
from rest_framework.exceptions import APIException
from rest_framework.exceptions import PermissionDenied
from rest_framework.exceptions import AuthenticationFailed
from socketio.exceptions import ConnectionRefusedError

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat.settings')

django.setup()

sio = socketio.AsyncServer(cors_allowed_origins='*', async_mode='aiohttp', logger=True)
app = web.Application()
sio.attach(app, socketio_path='/ws/chat/')

usersConnected = ConnectedUsers()

@sio.event
async def connect(sid, environ, auth):
    print(f"Client attempting to connect : {sid}")
    token = auth.get('token')
    chatId = auth.get('chatId')
    apiAnswer = None
    if token and chatId:
        try:
            print(f"Trying to authentificate : {sid}")
            apiAnswer = request_chat(endpoint_chat.fchat.format(chat_id=chatId), 'GET', None, token)
            print(f"Connection successeeded {sid}")
            await sio.emit('debug', apiAnswer, to=sid)
            await sio.enter_room(sid, str(chatId))
        except AuthenticationFailed:
            print(f"Authentification failed : {sid}")
            raise ConnectionRefusedError({"error": 401, "message": "Invalid token"})
        except  PermissionDenied:
            print(f"Permission denied : {sid}")
            raise ConnectionRefusedError({"error": 403, "message": "Permission denied"})
        except APIException:
            raise ConnectionRefusedError({"error": 500, "message": "error"})
        if apiAnswer: #and apiAnswer['chat_type'] == "private_message"
            usersConnected.add_user(apiAnswer['id'], sid, apiAnswer['username'], chatId, apiAnswer['chat_with'].get('id'))
    else:
        print(f"Connection failed : {sid}")
        raise ConnectionRefusedError({"error": 400, "message": "Missing args"})
    await sio.emit('message', {'author':'', 'content': 'You\'re now connected'}, to=sid)



@sio.event
async def disconnect(sid):
    usersConnected.remove_user(sid)
    print(f"Client disconnected : {sid}")

@sio.event
async def message(sid, data):
    chatId = usersConnected.get_chat_id(sid)
    username = userConnected.get_username(sid)
    content = data.get('content')
    token = data.get('token')
    print(f"New message from {sid}: {data}")
    if (content is None or token is None):
        await sio.emit(
            'error',
            {'error': 400, 'message': 'Invalid message format'},
            to=sid
        )
        return
    try:
        answerAPI = await sync_to_async(post_messages, thread_sensitive=False)(chatId, content, token)
        if usersConnected.is_chat_with_connected_with_him(sid) == False:
            await sio.emit(
                'debug',
                {'message': 'The other user is not connected'},
                to=sid
            )
        await sio.emit(
            'message',
            {'author':usersname, 'content': content},
            room=str(chatId)
        )
        print(f"Message saved and sent from {sid}: {data}")
    except PermissionDenied as e:
        await sio.emit(
            'error',
            {'error': 403, 'message': 'Permission Denied'},
            to=sid
        )
        print(f"Error: {e}")
        await sio.disconnect(sid)
    except AuthenticationFailed:
        print(f"Authentification failed : {sid}")
        if data.get('retry'):
            await sio.disconnect(sid)
        await sio.emit(
            'error',
            {'error': 401, 'message': 'Invalid token', 'retry_content': content},
            to=sid
        )
    except APIException:
        print(f"API error : {sid}")
        await sio.emit(
            'error',
            {'error': 500, 'message': 'error'},
            to=sid
        )
        await sio.disconnect(sid)

async def message_lobby(sid, data):
    chatId = usersConnected.get_chat_id(sid)
    username = usersConnected.get_username(sid)
    content = data.get('content')
    print(f"New message from {sid}: {data}")
    if (content is None):
        await sio.emit(
            'error',
            {'error': 400, 'message': 'Invalid message format'},
            to=sid
        )
        return
    await sio.emit(
        'message',
        {'author':username, 'content': content},
        room=str(chatId)
    )
    print(f"Message saved and sent from {sid}: {data}")



if __name__ == '__main__':
    web.run_app(app, port=8010)