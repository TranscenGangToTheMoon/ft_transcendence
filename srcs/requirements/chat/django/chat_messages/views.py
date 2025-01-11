from rest_framework import generics
from lib_transcendence.permissions import NotGuest
from lib_transcendence.serializer import SerializerAuthContext
from rest_framework.response import Response

from chat_messages.models import Messages
from chat_messages.serializers import MessagesSerializer
from chat_messages.utils import get_chat_participants


class RetrieveMessagesView(SerializerAuthContext, generics.ListAPIView):
    queryset = Messages.objects.all().order_by('-sent_at')
    serializer_class = MessagesSerializer
    permission_classes = [NotGuest]

    def filter_queryset(self, queryset):
        chat_id = self.kwargs['chat_id']

        user = get_chat_participants(chat_id, self.request.user.id, view_chat_required=False)
        if user.view_chat is False:
            user.set_view_chat()
        return queryset.filter(chat_id=chat_id)

    def list(self, request, *args, **kwargs):
        page = self.paginate_queryset(self.filter_queryset(self.get_queryset()))
        for message in page:
            if not message.is_read and message.author.id != request.user.id:
                message.read()
        return super().list(request, *args, **kwargs)


class CreateMessageView(SerializerAuthContext, generics.CreateAPIView):
    serializer_class = MessagesSerializer


retrieve_messages_view = RetrieveMessagesView.as_view()
create_message_view = CreateMessageView.as_view()
