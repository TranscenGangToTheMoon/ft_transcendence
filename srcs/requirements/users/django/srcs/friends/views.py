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


class FriendsRetrieveDeleteView(generics.RetrieveDestroyAPIView, FriendsMixin):
    lookup_field = 'pk'


friends_list_create_view = FriendsListCreateView.as_view()
friends_retrieve_delete_view = FriendsRetrieveDeleteView.as_view()
