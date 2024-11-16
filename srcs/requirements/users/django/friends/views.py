from lib_transcendence.exceptions import MessagesException
from rest_framework import generics
from rest_framework.exceptions import NotFound

from friends.models import Friends
from friends.serializers import FriendsSerializer


class FriendsMixin(generics.GenericAPIView):
    queryset = Friends.objects.all()
    serializer_class = FriendsSerializer


class FriendshipsView(generics.ListCreateAPIView, FriendsMixin):
    def filter_queryset(self, queryset):
        return queryset.filter(friends=self.request.user.id)


class FriendsDeleteView(generics.RetrieveDestroyAPIView, FriendsMixin):

    def get_object(self):
        try:
            return self.queryset.get(id=self.kwargs['friendship_id'], friends=self.request.user.id)
        except Friends.DoesNotExist:
            raise NotFound(MessagesException.NotFound.FRIENDSHIP)


friends_list_create_view = FriendshipsView.as_view()
friends_delete_view = FriendsDeleteView.as_view()
