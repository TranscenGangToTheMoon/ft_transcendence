# socket_server.py
import socketio
import sys

sio = socketio.AsyncServer(async_mode='eventlet')

@sio.event
async def connect(sid, environ):
    print('Client connected:', sid)
    await sio.emit('message', 'Bienvenue!', to=sid)

@sio.event
async def message(sid, data):
    print('received message from client:', data)
    await sio.emit('message', f'Reçu: {data}', to=sid)

@sio.event
async def disconnect(sid):
    print('Client disconnected:', sid)

if __name__ == '__main__':
	import eventlet
	app = socketio.WSGIApp(sio)
	eventlet.wsgi.server(eventlet.listen(('', sys.argv[1])), app)
