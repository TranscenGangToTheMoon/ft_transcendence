from rest_framework import generics
from lib_transcendence.serializer import SerializerAuthContext

from chat_messages.models import Messages
from chat_messages.serializers import MessagesSerializer
from chat_messages.utils import get_chat_participants


class RetrieveMessagesView(SerializerAuthContext, generics.ListAPIView):
    queryset = Messages.objects.all().order_by('-sent_at')
    serializer_class = MessagesSerializer

    def filter_queryset(self, queryset):
        chat_id = self.kwargs['chat_id']

        get_chat_participants(chat_id, self.request.user.id)
        return queryset.filter(chat_id=chat_id)


class CreateMessageView(SerializerAuthContext, generics.CreateAPIView):
    serializer_class = MessagesSerializer


retrieve_messages_view = RetrieveMessagesView.as_view()
create_message_view = CreateMessageView.as_view()
