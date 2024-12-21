from django.http import StreamingHttpResponse
from lib_transcendence.exceptions import ServiceUnavailable
from rest_framework.views import APIView
import redis

from users.auth import get_user

redis_client = redis.StrictRedis(host='redis')


class SSEView(APIView):

    @staticmethod
    def get(request, *args, **kwargs):
        def event_stream():
            user.connect()

            try:
                yield f"data: Successfully connected !\n\n" # todo remake message ?
                for message in pubsub.listen():
                    if message['type'] == 'message':
                        yield f"{message['data'].decode('utf-8')}\n\n"
            except GeneratorExit:
                pubsub.close() # todo remove channel
                user.disconnect()

            # try:
            #     while True:
            #         yield f"data: PING\n\n"
            #         message = pubsub.get_message(ignore_subscribe_messages=True)
            #         if message:
            #             yield f"data: {message['data'].decode('utf-8')}\n\n"
            #         time.sleep(1)
            # except GeneratorExit:
            #     user.disconnect()
            # finally:
            #     pubsub.close()

        user = get_user(request)
        try:
            pubsub = redis_client.pubsub()
            channel = f'events:user_{user.id}'
            pubsub.subscribe(channel)
        except redis.exceptions.ConnectionError:
            raise ServiceUnavailable('redis')

        response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        # response['Connection'] = 'keep-alive'
        return response


sse_view = SSEView.as_view()
