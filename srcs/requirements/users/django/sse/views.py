from rest_framework.views import APIView
from django.http import StreamingHttpResponse
import time


class SSEView(APIView):
    @staticmethod
    def event_stream(self):
        while True:
            time.sleep(1)
            yield f"data: {time.ctime()}\n\n"

    def get(self, request, *args, **kwargs):
        response = StreamingHttpResponse(self.event_stream(), content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        response['Connection'] = 'keep-alive'
        return response


sse_view = SSEView.as_view()
