
import os
import sys
import django
import asyncio
import socketio
from aiohttp import web
from asgiref.sync import async_to_sync, sync_to_async
from connectedUsers import ConnectedUsers
from lib_transcendence.auth import auth_verify
from lib_transcendence.chat import post_messages
from lib_transcendence.services import request_chat
from lib_transcendence.endpoints import Chat as endpoint_chat
from lib_transcendence.sse_events import create_sse_event, EventCode
from rest_framework.exceptions import APIException
from rest_framework.exceptions import PermissionDenied
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.exceptions import NotFound
from socketio.exceptions import ConnectionRefusedError

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat.settings')

sio = socketio.AsyncServer(cors_allowed_origins='*', async_mode='aiohttp', logger=True)
app = web.Application()
sio.attach(app, socketio_path='/ws/chat/')

usersConnected = ConnectedUsers()

@sio.event
async def connect(sid, environ, auth):
    print(f"Client attempting to connect : {sid}")
    token = auth.get('token')
    chatId = auth.get('chatId')
    chat_type = auth.get('chatType')
    user = None
    chat = None
    if token and chatId and chat_type:
        if chat_type != 'private_message' and chat_type != 'lobby':
            raise ConnectionRefusedError({"error": 400, "message": "Invalid chat type"})
        try:
            print(f"Trying to authentificate : {sid}")
            user = auth_verify(token)
            if (usersConnected.is_user_connected(user['id'])):
                print(f"User already connected : {sid}")
                await sio.disconnect(usersConnected.get_user_sid(user['id']))
            if chat_type == 'private_message':
                chat = request_chat(endpoint_chat.fchat.format(chat_id=chatId), 'GET', None, token)
                print(f"Connection successeeded {sid}")
                await sio.emit('debug', chat, to=sid)
            await sio.emit('debug', user, to=sid)
            await sio.enter_room(sid, str(chatId))
        except AuthenticationFailed:
            print(f"Authentification failed : {sid}")
            raise ConnectionRefusedError({"error": 401, "message": "Invalid token"})
        except  PermissionDenied:
            print(f"Permission denied : {sid}")
            raise ConnectionRefusedError({"error": 403, "message": "Permission denied"})
        except APIException:
            raise ConnectionRefusedError({"error": 500, "message": "error"})
        if user and chat:
            if chat_type == 'private_message':
                usersConnected.add_user(user['id'], sid, user['username'], chatId, chat_type, chat['chat_with'].get('id'))
            else:
                usersConnected.add_user(user['id'], sid, user['username'], chatId, chat_type)
    else:
        print(f"Connection failed : {sid}")
        raise ConnectionRefusedError({"error": 400, "message": "Missing args"})
    await sio.emit('debug', {'content': 'You\'re now connected'}, to=sid)



@sio.event
async def disconnect(sid):
    await sio.leave_room(sid, str(usersConnected.get_chat_id(sid)))
    usersConnected.remove_user(sid)
    print(f"Client disconnected : {sid}")

@sio.event
async def leave(sid, data):
    await sio.disconnect(sid)

@sio.event
async def message(sid, data):
    chatId = usersConnected.get_chat_id(sid)
    content = data.get('content')
    token = data.get('token')
    isChatWithConnected = usersConnected.is_chat_with_connected_with_him(sid)
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
        await sio.emit(
            'debug',
            answerAPI,
            to=sid
        )
        if (isChatWithConnected == False):
            await sio.emit(
                'debug',
                {'message': 'The other user is not connected'},
                to=sid
            )
            try:
                print(f"User not connected, sending sse {usersConnected.get_chat_with_id(sid)}")
                await sync_to_async(create_sse_event, thread_sensitive=False)(usersConnected.get_chat_with_id(sid), EventCode.RECEIVE_MESSAGE, answerAPI,{'username':usersConnected.get_user_id(sid),'message':content})
            except (PermissionDenied, AuthenticationFailed, NotFound, APIException) as e:
                print(f"Error SSE: {e}")
        else:
            await sio.emit(
                'debug',
                {'message': 'The other user is connected'},
                to=sid
            )
        await sio.emit(
            'message',
            {'author':answerAPI['author'], 'content': content, 'is_read': isChatWithConnected},
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
        usersConnected.remove_user(sid)
        await sio.disconnect(sid)
    except AuthenticationFailed:
        print(f"Authentification failed : {sid}")
        if data.get('retry'):
            usersConnected.remove_user(sid)
            await sio.disconnect(sid)
        await sio.emit(
            'error',
            {'error': 401, 'message': 'Invalid token', 'retry_content': content},
            to=sid
        )
    except NotFound:
        print(f"User not found : {sid}")
        await sio.emit(
            'error',
            {'error': 404, 'message': 'User not found'},
            to=sid
        )
        usersConnected.remove_user(sid)
        await sio.disconnect(sid)
    except APIException:
        print(f"API error : {sid}")
        await sio.emit(
            'error',
            {'error': 500, 'message': 'error'},
            to=sid
        )
        usersConnected.remove_user(sid)
        await sio.disconnect(sid)

async def message_lobby(sid, data):
    chatId = usersConnected.get_chat_id(sid)
    user = usersConnected.get_userId(sid)
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
        {'author':user, 'content': content},
        room=str(chatId)
    )
    print(f"Message saved and sent from {sid}: {data}")



if __name__ == '__main__':
    web.run_app(app, port=8010)