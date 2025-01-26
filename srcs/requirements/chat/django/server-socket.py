import os
import sys

import socketio
from aiohttp import web
from asgiref.sync import sync_to_async
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied, APIException, NotFound

from connectedUsers import ConnectedUsers
from lib_transcendence import endpoints
from lib_transcendence.auth import auth_verify
from lib_transcendence.chat import post_messages
from lib_transcendence.services import request_chat
from lib_transcendence.sse_events import create_sse_event, EventCode

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat.settings')

sio = socketio.AsyncServer(cors_allowed_origins='*', async_mode='aiohttp', logger=True)
app = web.Application()
sio.attach(app, socketio_path='/ws/chat/')

usersConnected = ConnectedUsers()


@sio.event
async def connect(sid, _, auth):
    print(f"Client attempting to connect : {sid}")
    token = auth.get('token')
    chat_id = auth.get('chatId')
    if token and chat_id:
        try:
            print(f"Trying to authentificate : {sid}")
            user = auth_verify(token)
            if usersConnected.is_user_connected(user['id']):
                print(f"User already connected : {sid}")
                await sio.emit('error', {'error': 409, 'message': 'User already connected'}, to=usersConnected.get_user_sid(user['id']))
                await sio.disconnect(usersConnected.get_user_sid(user['id']))
            chat = request_chat(endpoints.Chat.fchat.format(chat_id=chat_id), 'GET', token=token)
            print(f"Connection successeeded {sid}")
            await sio.emit('chat-server', {
                'content': 'You\'re now connected',
                'userData': user,
                'chatData': chat,
                }, to=sid)
            await sio.enter_room(sid, str(chat_id))
        except AuthenticationFailed:
            print(f"Authentification failed : {sid}")
            raise ConnectionRefusedError({"error": 401, "message": "Invalid token"})
        except PermissionDenied:
            print(f"Permission denied : {sid}")
            raise ConnectionRefusedError({"error": 403, "message": "Permission denied"})
        except APIException:
            raise ConnectionRefusedError({"error": 400, "message": "error"})
        if user and chat:
            usersConnected.add_user(user['id'], sid, user['username'], chat_id, chat['chat_with']['id'])
    else:
        print(f"Connection failed : {sid}")
        raise ConnectionRefusedError({"error": 400, "message": "Missing args"})


@sio.event
async def disconnect(sid):
    await sio.leave_room(sid, str(usersConnected.get_chat_id(sid)))
    usersConnected.remove_user(sid)
    print(f"Client disconnected : {sid}")


@sio.event
async def leave(sid, _):
    await sio.leave_room(sid, str(usersConnected.get_chat_id(sid)))
    usersConnected.remove_user(sid)
    await sio.disconnect(sid)


@sio.event
async def message(sid, data):
    chat_id = usersConnected.get_chat_id(sid)
    content = data.get('content')
    token = data.get('token')
    is_chat_with_connected = usersConnected.is_chat_with_connected_with_him(sid)
    print(f"New message from {sid}: {data}")
    if content is None or token is None:
        await sio.emit(
            'error',
            {'error': 400, 'message': 'Invalid message format'},
            to=sid
        )
        return
    try:
        answer_api = await sync_to_async(post_messages, thread_sensitive=False)(chat_id, content, token)
        await sio.emit(
            'chat-server',
            answer_api,
            to=sid
        )
        if not is_chat_with_connected:
            await sio.emit(
                'chat-server',
                {'message': 'The other user is not connected'},
                to=sid
            )
            print(f"User not connected, sending sse {usersConnected.get_chat_with_id(sid)}")
            await sync_to_async(create_sse_event, thread_sensitive=False)(usersConnected.get_chat_with_id(sid), EventCode.RECEIVE_MESSAGE, answer_api, {'username': usersConnected.get_user_id(sid), 'message': content}, False)
        else:
            await sio.emit(
                'chat-server',
                {'message': 'The other user is connected'},
                to=sid
            )
        await sio.emit(
            'message',
            {'author': answer_api['author'], 'content': content, 'is_read': is_chat_with_connected},
            room=str(chat_id)
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


if __name__ == '__main__':
    web.run_app(app, port=8010)
