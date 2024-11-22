import socketio


def init_socketIO(sio):
    def connect_handler(sid, environ, auth):
        print(f"Client connected: {sid}")
        # try:
        #     token = auth.get('token')
        #     if not token:
        #         print('No token provided')
        #         return False
        # except Exception as e:
        #     print(f"Error during authentication: {e}")
        #     return False
        # return True
    sio.on('connect', namespace='/game', handler=connect_handler)

    @sio.event
    async def chat_message(sid, data):
        print("message ", data)

    async def broadcast_message(message):
        await sio.emit('message', {'data': message})

    @sio.event
    def disconnect(sid):
        print('disconnect ', sid)
