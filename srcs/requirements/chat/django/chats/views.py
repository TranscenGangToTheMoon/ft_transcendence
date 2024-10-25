from rest_framework import generics

from chats.models import Chats, ChatParticipants
from chats.serializers import ChatsSerializer


class ChatsMixin(generics.GenericAPIView):
    queryset = Chats.objects.all()
    serializer_class = ChatsSerializer

    def filter_queryset(self, queryset):
        join_chats = ChatParticipants.objects.filter(user_id=self.request.user.id).values_list('chat_id', flat=True)
        return queryset.filter(id__in=join_chats)


class ChatsListCreateView(generics.ListCreateAPIView, ChatsMixin):
    pass


class ChatsRetrieveDeleteView(generics.RetrieveDestroyAPIView, ChatsMixin):
    lookup_field = 'pk'


chats_list_create_view = ChatsListCreateView.as_view()
chats_retrieve_delete_view = ChatsRetrieveDeleteView.as_view()
