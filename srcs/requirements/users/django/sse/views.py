from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import StreamingHttpResponse
import time


class SSEManager:
    clients = []

    @classmethod
    def add_client(cls, response):
        cls.clients.append(response)

    @classmethod
    def remove_client(cls, response):
        cls.clients.remove(response)

    @classmethod
    def send_message(cls, message):
        for client in cls.clients:
            client.write(f"data: {message}\n\n")
            client.flush()


def event_stream():
    while True:
        time.sleep(1)  # Simulez un délai pour l'exemple
        yield "data: {}\n\n".format("Hello from SSE!")


class SSEView(APIView):

    def get(self, request, *args, **kwargs):
        def event_stream():
            try:
                for i in range(1, 1000):
                    yield f"data: still connected\n\n"
                    time.sleep(10)
            except GeneratorExit:
                print("Connexion SSE terminée.")

        print(self.request.user)
        response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        response['Connection'] = 'keep-alive'
        SSEManager.add_client(response)
        try:
            return response
        finally:
            SSEManager.remove_client(response)


class NotificationView(APIView):

    @staticmethod
    def post(self, request):
        message = request.data.get('message')
        if message:
            SSEManager.send_message(message)
            return Response({"status": "Notification sent"}, status=status.HTTP_201_CREATED)
        return Response({"error": "Message is required"}, status=status.HTTP_400_BAD_REQUEST)


sse_view = SSEView.as_view()
