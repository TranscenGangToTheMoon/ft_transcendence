from rest_framework.generics import CreateAPIView

from events.serializer import EventSerializer


class EnventsAPIView(CreateAPIView):
    authentication_classes = []
    serializer_class = EventSerializer


events_view = EnventsAPIView.as_view()
