
import socketio
import asyncio
from aiohttp import web

# sio = socketio.AsyncServer(cors_allowed_origins='*')
# app = web.Application()
# sio.attach(app)

sio = socketio.AsyncServer(cors_allowed_origins='*', async_mode='aiohttp', logger=True)
app = web.Application()
sio.attach(app, socketio_path='/ws/chat/')

@sio.event
async def connect(sid, environ):
    print(f"Client connected : {sid}")
    await sio.emit('message', {'message': '<em>Welcome!</em>',}, to=sid)


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