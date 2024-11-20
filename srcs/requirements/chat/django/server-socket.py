
import socketio
from aiohttp import web

sio = socketio.AsyncServer(cors_allowed_origins='*')
app = web.Application()
sio.attach(app)


@sio.event
async def connect(sid, environ):
    print(f"Client connected : {sid}")
    sio.emit('message', {'data': 'Welcome!'}, to=sid)


@sio.event
async def disconnect(sid):
    print(f"Client disconnected : {sid}")


@sio.event
async def message(sid, data):
    print(f"New message from {sid}: {data}")
    sio.emit('message', {'data': 'Message received!'})


if __name__ == '__main__':
    web.run_app(app, port=8002)