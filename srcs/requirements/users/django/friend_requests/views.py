from rest_framework import generics

from friend_requests.models import FriendRequests
from friend_requests.serializers import FriendRequestsSerializer


class FriendRequestsMixin(generics.GenericAPIView):
    queryset = FriendRequests.objects.all()
    serializer_class = FriendRequestsSerializer


class FriendRequestsListCreateView(generics.ListCreateAPIView, FriendRequestsMixin):

    def filter_queryset(self, queryset):
        return queryset.filter(sender=self.request.user.id)


class FriendRequestsReceiveListView(generics.ListAPIView, FriendRequestsMixin):

    def filter_queryset(self, queryset):
        return queryset.filter(receiver=self.request.user.id)


class FriendRequestsDeleteView(generics.RetrieveDestroyAPIView, FriendRequestsMixin):
    lookup_field = 'friend_request_id'


friend_requests_list_create_view = FriendRequestsListCreateView.as_view()
friend_requests_receive_list_view = FriendRequestsReceiveListView.as_view()
friend_requests_delete_view = FriendRequestsDeleteView.as_view()
