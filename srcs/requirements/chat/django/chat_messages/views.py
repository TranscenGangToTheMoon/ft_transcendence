from rest_framework import generics
from lib_transcendence.serializer import SerializerAuthContext

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


messages_view = MessagesView.as_view()
