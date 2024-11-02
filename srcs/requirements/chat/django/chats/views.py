from rest_framework import generics
from rest_framework.exceptions import MethodNotAllowed

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
            return queryset.filter(id__in=join_chats, participants__username__icontains=query, blocked=False)
        return queryset.filter(id__in=join_chats, blocked=False)


class ChatsView(generics.ListCreateAPIView, ChatsMixin):
    pass


class ChatView(generics.RetrieveUpdateDestroyAPIView, ChatsMixin):
    lookup_field = 'pk'

    def destroy(self, request, *args, **kwargs):
        if self.request.get_host().split(':')[0] != 'game': #todo in librairy
            raise MethodNotAllowed(request.method)
        return super().destroy(request, *args, **kwargs)


chats_view = ChatsView.as_view()
chat_view = ChatView.as_view()
