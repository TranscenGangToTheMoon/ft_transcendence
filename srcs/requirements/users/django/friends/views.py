from rest_framework import generics

from friends.models import Friends
from friends.serializers import FriendsSerializer


class FriendsMixin(generics.GenericAPIView):
    queryset = Friends.objects.all()
    serializer_class = FriendsSerializer

    def filter_queryset(self, queryset):
        return queryset.filter(friends=self.request.user.id)


class FriendsListCreateView(generics.ListCreateAPIView, FriendsMixin):
    pass


class FriendsDeleteView(generics.DestroyAPIView, FriendsMixin):
    lookup_field = 'friendship_id'


friends_list_create_view = FriendsListCreateView.as_view()
friends_delete_view = FriendsDeleteView.as_view()
