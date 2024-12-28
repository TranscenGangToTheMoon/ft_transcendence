import asyncio
import time

from asgiref.sync import sync_to_async
from django.http import StreamingHttpResponse
from lib_transcendence.exceptions import MessagesException, ServiceUnavailable, ResourceExists
from lib_transcendence.sse_events import EventCode
from lib_transcendence.auth import AsyncAuthentication
from rest_framework import renderers
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
import redis

from sse.events import publish_event
from users.auth import get_user


redis_client = redis.StrictRedis(host='event-queue')
ENDLINE = '\n\n'



# async def streaming_response():
#     try:
#         # Do some work here
#         async for chunk in my_streaming_iterator():
#             yield chunk
#     except asyncio.CancelledError:
#         # Handle disconnect
#         ...
#         raise


# async def my_streaming_view(request):
#     return StreamingHttpResponse(streaming_response())

class EventStreamRenderer(renderers.BaseRenderer):
    media_type = 'text/event-stream'
    format = 'text-event-stream'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data


class SSEView(APIView):
    renderer_classes = [EventStreamRenderer]
    # authentication_classes = [AsyncAuthentication]

    @staticmethod
    def get(request, *args, **kwargs):
        print('REQUEST', request, flush=True)
        # todo when serveur up set all is_connected False

        def event_stream(_user, _channel):
            async def async_event_stream():
                pubsub = redis_client.pubsub()
                await pubsub.subscribe(_channel)

                try:
                    async for message in pubsub.listen():
                        print(message, flush=True)
                        if message['type'] == 'message':
                            event, data = message['data'].decode('utf-8').split(':', 1)
                            print(event, flush=True)
                            if event == EventCode.CONNECTION_CLOSE:
                                print('caca', flush=True)
                                raise PermissionDenied(MessagesException.PermissionDenied.CONNECTION_CLOSE)
                            yield f'event: {event}\ndata: {data}\n\n'
                        # await asyncio.sleep(0.1)
                except asyncio.CancelledError:
                    await pubsub.unsubscribe(_channel)
                    await pubsub.close()

            return sync_to_async(async_event_stream)()

        # try:
            #     while True:
            #         # Lecture asynchrone des messages
            #         message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            #
            #         if request.stream.is_closing():  # Détection de la déconnexion utilisateur
            #             print(f"User {request.user.id} disconnected")
            #             break
            #
            #         if message:
            #             # Envoyer le message au client
            #             yield f"data: {message['data'].decode('utf-8')}\n\n"
            #
            #         # Ajouter une pause pour éviter une boucle infinie trop rapide
            #         await asyncio.sleep(0.1)
            # finally:
            #     await pubsub.unsubscribe(user_channel)
            #     await pubsub.close()
            #     await redis.close()

        # def event_stream(_user, _channel):
        #     publish_event(_user, EventCode.CONNECTION_SUCCESS) # todo useless
        # #todo remake user system, don't use request.user
        #     # try:
        #     #     for message in pubsub.listen():
        #     #         if message['type'] == 'message':
        #     #             yield f"{message['data'].decode('utf-8')}\n\n"
        #     # except GeneratorExit:
        #     #     pubsub.close()
        #     #     _user.disconnect()
        #     try:
        #         for message in pubsub.listen():
        #             print(message, flush=True)
        #             if message['type'] == 'message':
        #                 event, data = message['data'].decode('utf-8').split(':', 1)
        #                 print(event, flush=True)
        #                 if event == EventCode.CONNECTION_CLOSE:
        #                     print('caca', flush=True)
        #                     raise PermissionDenied(MessagesException.PermissionDenied.CONNECTION_CLOSE)
        #                 yield f'event: {event}\ndata: {data}\n\n'
        #     # try:
        #     #     while True:
        #     #         message = pubsub.get_message(ignore_subscribe_messages=True)
        #     #         if message:
        #     #             event, data = message['data'].decode('utf-8').split(':', 1)
        #     #             print(event, flush=True)
        #     #             if event == EventCode.CONNECTION_CLOSE:
        #     #                 print('caca', flush=True)
        #     #                 raise PermissionDenied(MessagesException.PermissionDenied.CONNECTION_CLOSE)
        #     #         else:
        #     #             data = 'PING'
        #     #             event = 'ping'
        #     #         yield f'event: {event}\ndata: {data}\n\n'
        #     #         time.sleep(1)
        #     except GeneratorExit:
        #         pass
        #     pubsub.close()
        #     if redis_client.get(_channel) is None: # todo didn't work
        #         _user.disconnect()

        user = get_user(request)
        user.connect()
        channel = f'events:user_{user.id}'

        # try:
        #     pubsub = redis_client.pubsub()
        #     channel = f'events:user_{user.id}'
        #     pubsub.subscribe(channel)
        # except redis.exceptions.ConnectionError:
        #     raise ServiceUnavailable('event-queue')

        response = StreamingHttpResponse(event_stream(user, channel), content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        return response

pubsub = redis_client.pubsub()
pubsub.subscribe('_channel')


async def streaming_response():
    try:
        async for message in pubsub.listen():
            if message['type'] == 'message':
                event, data = message['data'].decode('utf-8').split(':', 1)
                yield f'event: {event}\ndata: {data}\n\n'
    except asyncio.CancelledError:
        print('DISCONNECTED', flush=True)
        raise


async def sse_view(request):
    return StreamingHttpResponse(streaming_response())

# sse_view = SSEView.as_view()
