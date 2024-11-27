# socket_server.py
import socketio
import django
import os
from django.core.asgi import get_asgi_application
from socketio import ASGIApp

# Configurer Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'websocket.settings')
django.setup()

# Créer une instance Socket.IO en mode asynchrone compatible ASGI
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
django_app = get_asgi_application()
application = ASGIApp(sio, django_app)

# Gérer la connexion des clients
@sio.event
async def connect(sid, environ):
    print('Client connected:', sid)
    await sio.emit('message', 'Bienvenue!', to=sid)

# Gérer les messages du client
@sio.event
async def message(sid, data):
    print('received message from client:', data)
    await sio.emit('message', f'Reçu: {data}', to=sid)

# Gérer la déconnexion
@sio.event
async def disconnect(sid):
    print('Client disconnected:', sid)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(application, host='0.0.0.0', port=8000)
