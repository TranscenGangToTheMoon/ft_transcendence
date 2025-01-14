import json
import time
from threading import Thread

from django.http import StreamingHttpResponse
from lib_transcendence.exceptions import ServiceUnavailable
from lib_transcendence.sse_events import EventCode
from rest_framework import renderers
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView
import redis

from sse.events import publish_event
from users.auth import get_user


redis_client = redis.StrictRedis(host='event-queue')
ENDLINE = '\n\n'


class ConnectionClose(Exception):
    pass


class EventStreamRenderer(renderers.BaseRenderer):
    media_type = 'text/event-stream'
    format = 'text-event-stream'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data


class SSEView(APIView):
    renderer_classes = [EventStreamRenderer]

    @staticmethod
    def get(request, *args, **kwargs):

        def event_stream(_user_id, _channel):
            try:
                while True:
                    for message in pubsub.listen():
                        if message['type'] == 'message':
                            print('message', _user_id, message['data'], flush=True)
                            event, data = message['data'].decode('utf-8').split(':', 1)
                            if event == EventCode.DELETE_USER:
                                raise ConnectionClose
                            if event == EventCode.GAME_START:
                                get_user(id=_user_id).set_game_playing(json.loads(data)['data']['code'])
                            yield f'event: {event}\ndata: {data}\n\n'
            except (GeneratorExit, ConnectionClose) as e:
                pubsub.close()
                if isinstance(e, GeneratorExit):
                    try:
                        result = redis_client.pubsub_numsub(_channel)[0][1]
                        if not result:
                            get_user(id=_user_id).disconnect()
                    except (IndexError, NotFound):
                        pass

        user = get_user(request)
        if user.connect():
            Thread(target=ping_loop, args=(user, )).start()
        user_id = user.id
        del user

        try:
            pubsub = redis_client.pubsub()
            channel = f'events:user_{user_id}'
            pubsub.subscribe(channel)
        except redis.exceptions.ConnectionError:
            raise ServiceUnavailable('event-queue')

        response = StreamingHttpResponse(event_stream(user_id, channel), content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        return response


def ping_loop(user):
    for _ in range(1000000): # TODO fguirama: remake
        publish_event(user, EventCode.PING, 'PING')
        time.sleep(1)


sse_view = SSEView.as_view()
