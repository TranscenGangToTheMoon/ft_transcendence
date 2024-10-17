from rest_framework import generics

from chat_messages.models import Messages
from chat_messages.serializers import MessagesSerializer
from chats.models import ChatParticipants


class MessagesListCreateView(generics.ListCreateAPIView):
    queryset = Messages.objects.all().order_by('-sent_at')
    serializer_class = MessagesSerializer
    lookup_field = 'pk'

    def filter_queryset(self, queryset):
        pk = self.kwargs.get('pk')
        if pk is not None:
            chat = ChatParticipants.objects.filter(chat_id=pk, user_id=self.request.user.id)
            if chat.exists():
                return queryset.filter(chat_id=pk)
        return queryset.none()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['pk'] = self.kwargs.get('pk')
        context['auth_user'] = self.request.data['auth_user']
        return context


messages_list_create_view = MessagesListCreateView.as_view()
