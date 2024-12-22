from django.db.models import Q
from lib_transcendence.exceptions import MessagesException
from lib_transcendence.serializer import SerializerKwargsContext
from rest_framework import generics
from rest_framework.exceptions import NotFound

from friend_requests.models import FriendRequests
from friend_requests.serializers import FriendRequestsSerializer
from friends.serializers import FriendsSerializer
from sse.events import publish_event


class FriendRequestsMixin(generics.GenericAPIView):
    queryset = FriendRequests.objects.all()
    serializer_class = FriendRequestsSerializer


class FriendRequestsListCreateView(generics.ListCreateAPIView, FriendRequestsMixin):

    def filter_queryset(self, queryset):
        return queryset.filter(sender=self.request.user.id)

    def perform_create(self, serializer):
        super().perform_create(serializer)

        receiver = serializer.instance.receiver
        if receiver.is_online:
            publish_event(receiver.id, 'friends', 'receive-friend-requests', data=serializer.data)


class FriendRequestsReceiveListView(generics.ListAPIView, FriendRequestsMixin):

    def filter_queryset(self, queryset):
        return queryset.filter(receiver=self.request.user.id)

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        self.filter_queryset(self.queryset).update(new=False)
        return response


class FriendRequestView(SerializerKwargsContext, generics.CreateAPIView, generics.RetrieveDestroyAPIView, FriendRequestsMixin):

    def get_object(self):
        try:
            return self.queryset.get(Q(sender=self.request.user.id) | Q(receiver=self.request.user.id), id=self.kwargs['friend_request_id'])
        except FriendRequests.DoesNotExist:
            raise NotFound(MessagesException.NotFound.FRIEND_REQUEST)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return FriendsSerializer
        return super().get_serializer_class()


friend_requests_list_create_view = FriendRequestsListCreateView.as_view()
friend_requests_receive_list_view = FriendRequestsReceiveListView.as_view()
friend_request_view = FriendRequestView.as_view()
