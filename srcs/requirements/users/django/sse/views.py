from rest_framework.views import APIView
from django.http import StreamingHttpResponse
import time


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
        return response


sse_view = SSEView.as_view()
