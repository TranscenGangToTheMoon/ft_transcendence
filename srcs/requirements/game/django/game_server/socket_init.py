def init_socketIO(server, sio):
    # Gérer les événements Socket.IO
    @sio.event
    async def connect(sid, environ):
        print(f"Client connecté : {sid}")
        await sio.emit("response", {"message": "Bienvenue !"}, room=sid)

    @sio.event
    async def chat_message(sid, data):
        print("message ", data)

    @sio.event
    def create_match(sid, message):
        if sid == server.django_sid and sid != -1:
            server.launch_game(message.get('match_code'))

    @sio.event
    def disconnect(sid):
        print('disconnected', sid)
