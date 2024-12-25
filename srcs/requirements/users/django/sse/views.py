import time

from django.http import StreamingHttpResponse
from lib_transcendence.exceptions import MessagesException, ServiceUnavailable, ResourceExists
from lib_transcendence.sse_events import EventCode
from rest_framework.views import APIView
import redis

from sse.events import publish_event
from users.auth import get_user
from sse.events import ping


redis_client = redis.StrictRedis(host='event-queue')
ENDLINE = '\n\n'


class SSEView(APIView):

    @staticmethod
    def get(request, *args, **kwargs):
        def event_stream(_user):
            _user.connect()
            publish_event(_user.id, EventCode.CONNECTION_SUCCESS)

            # try:
            #     for message in pubsub.listen():
            #         if message['type'] == 'message':
            #             yield f"{message['data'].decode('utf-8')}\n\n"
            # except GeneratorExit:
            #     pubsub.close()
            #     _user.disconnect()
            ping_str = ping.dumps() + ENDLINE
            try:
                while True:
                    message = pubsub.get_message(ignore_subscribe_messages=True)
                    if message:
                        print(f'MESSAGE {_user.id}', flush=True)
                        yield message['data'].decode('utf-8') + ENDLINE
                    else:
                        print(f'PING {_user.id}', flush=True)
                        yield ping_str
                    time.sleep(1)
            except GeneratorExit:
                pass
            pubsub.close()
            _user.disconnect()

        user = get_user(request)
        if user.is_online:
            raise ResourceExists(MessagesException.ResourceExists.SSE)

        try:
            pubsub = redis_client.pubsub()
            channel = f'events:user_{user.id}'
            pubsub.subscribe(channel)
        except redis.exceptions.ConnectionError:
            raise ServiceUnavailable('event-queue')

        response = StreamingHttpResponse(event_stream(user), content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        # response['Connection'] = 'keep-alive'
        return response


sse_view = SSEView.as_view()
