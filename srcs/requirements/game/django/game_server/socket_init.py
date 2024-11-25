def init_socketIO(sio):

    @sio.event
    async def chat_message(sid, data):
        print("message ", data)

    async def broadcast_message(message):
        await sio.emit('message', {'data': message})

    @sio.event
    def disconnect(sid):
        print('disconnect ', sid)
