from lib_transcendence.serializer import SerializerAuthContext
from lib_transcendence.utils import get_host
from lib_transcendence.permissions import NotGuest
from rest_framework import generics, status
from rest_framework.response import Response

from chat_messages.utils import get_chat_participants
from chats.models import Chats, ChatParticipants
from chats.serializers import ChatsSerializer


class ChatsView(generics.ListCreateAPIView):
    serializer_class = ChatsSerializer
    permission_classes = [NotGuest]

    def get_queryset(self):
        query = self.request.query_params.get('q')
        if query == '':
            query = None
        kwars = {'user_id': self.request.user.id}
        if query is None:
            kwars['view_chat'] = True
        join_chats = ChatParticipants.objects.filter(**kwars).values_list('chat_id', flat=True)
        if query is not None:
            join_chats = ChatParticipants.objects.exclude(user_id=self.request.user.id).filter(chat_id__in=join_chats, username__icontains=query).values_list('chat_id', flat=True)
        return Chats.objects.filter(id__in=join_chats, blocked=False).distinct().order_by('-last_updated')


class ChatView(SerializerAuthContext, generics.RetrieveDestroyAPIView):
    permission_classes = [NotGuest]
    serializer_class = ChatsSerializer
    lookup_field = 'chat_id'

    def get_object(self):
        user = get_chat_participants(self.kwargs['chat_id'], self.request.user.id, False)
        if self.request.method == 'GET' and user.view_chat is False:
            user.set_view_chat()
        return user.chat

    def destroy(self, request, *args, **kwargs):
        if get_host(request) not in ('game', 'users'):
            user = get_chat_participants(kwargs['chat_id'], request.user.id, False)
            user.set_view_chat(False)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return super().destroy(request, *args, **kwargs)


class GetChatNotifications(generics.RetrieveAPIView):
    authentication_classes = []

    def retrieve(self, request, *args, **kwargs):
        user_id = self.kwargs['user_id']
        count = 0

        for chat in Chats.objects.filter(participants__user_id=user_id):
            if chat.messages.exclude(author=user_id).filter(is_read=False).exists():
                count += 1

        return Response({'notifications': count})


chats_view = ChatsView.as_view()
chat_view = ChatView.as_view()
get_chat_notifications_view = GetChatNotifications.as_view()
