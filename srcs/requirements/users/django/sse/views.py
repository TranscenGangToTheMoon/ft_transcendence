from lib_transcendence.exceptions import MessagesException
from rest_framework import status
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import StreamingHttpResponse
import time

from users.auth import get_user
from users.models import Users


# SSE Usage
#  - user join lobby
#  - user leave lobby
#  - user set ready lobby
#  - game start lobby
#  - user join tournament
#  - user leave tournament
#  - game start lobby
#  - game not start lobby
#  - friend request
#  - accept friend request
#  - chat notification
#  - friend status update ?
#  - game port


class SSEManager:
    clients = {}

    @classmethod
    def add_client(cls, user, response):
        print('NEW USER CONNECTED:', user.id, flush=True)
        cls.clients[user.id] = {'user': user, 'response': response}

    @classmethod
    def remove_client(cls, user_id):
        print('USER DISCONNECTED:', user_id, flush=True)
        cls.clients.pop(user_id)

    @classmethod
    def send_message(cls, user_id, message):
        print(cls.clients, flush=True)
        print('USER SENT MESSAGE:', user_id, message, flush=True)
        if user_id not in cls.clients:
            print('USER NOT CONNECTED:', user_id, flush=True)
            return
        client = cls.clients[user_id]['response']
        client.write(f"data: {message}\n\n")
        client.flush()


def event_stream(user):
    while True:
        time.sleep(10)
        yield "data: {}\n\n".format("Hello from SSE! " + user.username)


class SSEView(APIView):

    def get(self, request, *args, **kwargs):
        user = get_user(self.request)
        response = StreamingHttpResponse(event_stream(user), content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        SSEManager.add_client(user, response)
        # try:
        return response
        # finally:
        #     SSEManager.remove_client(user.id)


class NotificationView(APIView):

    @staticmethod
    def post(request):
        # message = 'coucou mon ptit loulou'
        message = request.data.get('message')
        if message is None:
            raise ParseError({'detail': [MessagesException.ValidationError.FIELD_REQUIRED]})
        user_to = request.data.get('user_to')
        if user_to is None:
            raise ParseError({'detail': [MessagesException.ValidationError.FIELD_REQUIRED]})
        SSEManager.send_message(user_to, message)
        return Response({"status": "Notification sent"}, status=status.HTTP_201_CREATED)


class EventView(APIView):

    def post(self, request):
        # message = 'coucou mon ptit loulou'
        message = request.data.get('message')
        if message is None:
            raise ParseError({'detail': [MessagesException.ValidationError.FIELD_REQUIRED]})
        user_to = request.data.get('user_to')
        if user_to is None:
            raise ParseError({'detail': [MessagesException.ValidationError.FIELD_REQUIRED]})
        if message:
            SSEManager.send_message(user_to, message)
            return Response({"status": "Notification sent"}, status=status.HTTP_201_CREATED)
        return Response({"error": "Message is required"}, status=status.HTTP_400_BAD_REQUEST)


sse_view = SSEView.as_view()
notification_view = NotificationView.as_view()
event_view = EventView.as_view()
