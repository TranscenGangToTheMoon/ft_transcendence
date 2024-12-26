import time

from django.http import StreamingHttpResponse
from lib_transcendence.exceptions import MessagesException, ServiceUnavailable, ResourceExists
from lib_transcendence.sse_events import EventCode
from rest_framework import renderers
from rest_framework.views import APIView

import redis

from sse.events import publish_event
from users.auth import get_user


redis_client = redis.StrictRedis(host='event-queue')
ENDLINE = '\n\n'


class EventStreamRenderer(renderers.BaseRenderer):
    media_type = 'text/event-stream'
    format = 'text-event-stream'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data

class SSEView(APIView):
    renderer_classes = [EventStreamRenderer]

    @staticmethod
    def get(request, *args, **kwargs):
        # todo when serveur up set all is_connected False
        def event_stream(_user_id, _channel):
            publish_event(_user_id, EventCode.CONNECTION_SUCCESS) # todo useless

            # try:
            #     for message in pubsub.listen():
            #         if message['type'] == 'message':
            #             yield f"{message['data'].decode('utf-8')}\n\n"
            # except GeneratorExit:
            #     pubsub.close()
            #     _user.disconnect()
            try:
                while True:
                    message = pubsub.get_message(ignore_subscribe_messages=True)
                    if message:
                        event, data = message['data'].decode('utf-8').split(':', 1)
                    else:
                        data = 'PING'
                        event = 'ping'
                    yield f'event: {event}\ndata: {data}\n\n'
                    time.sleep(1)
            except GeneratorExit:
                pass
            pubsub.close()
            if redis_client.get(_channel) is None:
                _user = get_user(request)
                _user.disconnect()

        user = get_user(request)
        user.connect()
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
        # response['Connection'] = 'keep-alive'
        return response

sse_view = SSEView.as_view()
