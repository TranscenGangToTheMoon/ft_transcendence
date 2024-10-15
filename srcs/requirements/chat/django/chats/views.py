from rest_framework import generics

from chats.models import Chats, ChatParticipants
from chats.serializers import ChatsSerializer


class ChatsMixin(generics.GenericAPIView):
    queryset = Chats.objects.all()
    serializer_class = ChatsSerializer

    def filter_queryset(self, queryset):
        join_chats = ChatParticipants.objects.filter(user=self.request.user.id)
        return queryset.filter(id__in=join_chats)


class ChatsListCreateView(generics.ListCreateAPIView, ChatsMixin):
    pass


class ChatsDeleteView(generics.DestroyAPIView, ChatsMixin):
    lookup_field = 'pk'


friends_list_create_view = ChatsListCreateView.as_view()
friends_delete_view = ChatsDeleteView.as_view()
