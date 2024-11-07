from rest_framework import generics
from rest_framework.exceptions import PermissionDenied

from chat_messages.models import Messages
from chat_messages.serializers import MessagesSerializer
from chats.models import ChatParticipants


class MessagesView(generics.ListCreateAPIView):
    queryset = Messages.objects.all().order_by('-sent_at')
    serializer_class = MessagesSerializer
    lookup_field = 'pk'

    def filter_queryset(self, queryset):
        pk = self.kwargs.get('pk')
        if pk is None:
            raise serializers.ValidationError('Pk is required.')
        try:
            ChatParticipants.objects.get(chat_id=pk, user_id=self.request.user.id)
            return queryset.filter(chat_id=pk)
        except ChatParticipants.DoesNotExist:
            raise PermissionDenied(MessagesException.PermissionDenied.NOT_BELONG_TO_CHAT)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['pk'] = self.kwargs.get('pk')
        context['auth_user'] = self.request.data['auth_user']
        return context


messages_view = MessagesView.as_view()
