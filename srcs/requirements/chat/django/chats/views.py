from django.http import Http404
from lib_transcendence.utils import get_host
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
            join_chats = ChatParticipants.objects.exclude(user_id=self.request.user.id).filter(chat_id__in=join_chats, username__icontains=query).values_list('chat_id', flat=True)
        return queryset.filter(id__in=join_chats, blocked=False).distinct()


class ChatsView(generics.ListCreateAPIView, ChatsMixin):
    pass


class ChatView(generics.RetrieveUpdateDestroyAPIView, ChatsMixin):
    lookup_field = 'pk'

    def get_object(self):
        obj = super().get_object()
        if obj.blocked:
            raise Http404
        return obj

    def destroy(self, request, *args, **kwargs):
        if get_host(request) != 'game':
            raise MethodNotAllowed(request.method)
        return super().destroy(request, *args, **kwargs)


chats_view = ChatsView.as_view()
chat_view = ChatView.as_view()
