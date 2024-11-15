from lib_transcendence.serializer import SerializerContext
from lib_transcendence.utils import get_host
from rest_framework import generics
from rest_framework.exceptions import MethodNotAllowed

from chat_messages.utils import get_chat_participants
from chats.models import Chats, ChatParticipants
from chats.serializers import ChatsSerializer


class ChatsMixin(generics.GenericAPIView):
    queryset = Chats.objects.all()
    serializer_class = ChatsSerializer

    def filter_queryset(self, queryset):
        query = self.request.data.pop('q', None)
        kwars = {'user_id': self.request.user.id}
        if query is None:
            kwars['view_chat'] = True
        join_chats = ChatParticipants.objects.filter(**kwars).values_list('chat_id', flat=True)
        if query is not None:
            join_chats = ChatParticipants.objects.exclude(user_id=self.request.user.id).filter(chat_id__in=join_chats, username__icontains=query).values_list('chat_id', flat=True)
        return queryset.filter(id__in=join_chats, blocked=False).distinct()


class ChatsView(generics.ListCreateAPIView, ChatsMixin):
    pass


class ChatView(SerializerContext, generics.RetrieveUpdateDestroyAPIView, ChatsMixin):
    lookup_field = 'chat_id'

    def get_object(self):
        user = get_chat_participants(self.kwargs['chat_id'], self.request.user.id, False)
        if user.view_chat is False:
            user.set_view_chat()
        return user.chat

    def destroy(self, request, *args, **kwargs):
        if get_host(request) not in ('game', 'users'):
            raise MethodNotAllowed(request.method)
        return super().destroy(request, *args, **kwargs)


chats_view = ChatsView.as_view()
chat_view = ChatView.as_view()
