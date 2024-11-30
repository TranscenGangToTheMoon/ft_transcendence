from rest_framework import generics
from rest_framework.exceptions import MethodNotAllowed
from lib_transcendence.serializer import SerializerAuthContext
from lib_transcendence.utils import get_host

from chat_messages.models import Messages
from chat_messages.serializers import MessagesSerializer
from chat_messages.utils import get_chat_participants


class MessagesView(SerializerAuthContext, generics.ListCreateAPIView):
    queryset = Messages.objects.all().order_by('-sent_at')
    serializer_class = MessagesSerializer

    def filter_queryset(self, queryset):
        chat_id = self.kwargs['chat_id']

        get_chat_participants(chat_id, self.request.user.id)
        return queryset.filter(chat_id=chat_id)

    def create(self, request, *args, **kwargs):
        if get_host(request) != 'chat':
            raise MethodNotAllowed('POST')
        return super().create(request, *args, **kwargs)


messages_view = MessagesView.as_view()
# todo make endpoint for read messages
