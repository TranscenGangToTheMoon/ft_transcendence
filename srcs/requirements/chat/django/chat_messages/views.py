from rest_framework import generics
from lib_transcendence.serializer import SerializerContext

from chat_messages.models import Messages
from chat_messages.serializers import MessagesSerializer
from chats.models import ChatParticipants


class MessagesView(SerializerContext, generics.ListCreateAPIView):
    queryset = Messages.objects.all().order_by('-sent_at')
    serializer_class = MessagesSerializer
    lookup_field = 'pk'

    def filter_queryset(self, queryset):
        chat_id = self.kwargs['chat_id']



messages_view = MessagesView.as_view()
