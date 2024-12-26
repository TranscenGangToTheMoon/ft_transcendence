from django.db.models import Q
from lib_transcendence.exceptions import MessagesException
from lib_transcendence.serializer import SerializerKwargsContext
from lib_transcendence.sse_events import EventCode
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
            publish_event(receiver.id, EventCode.RECEIVE_FRIEND_REQUEST, data={'username': serializer.data['sender']['username'], **serializer.data}) # todo remake with field format


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

    def perform_create(self, serializer):
        super().perform_create(serializer)

        sender_friend_request = serializer.instance.friends.exclude(id=self.request.user.id).first()
        if sender_friend_request.is_online:
            publish_event(sender_friend_request.id, EventCode.ACCEPT_FRIEND_REQUEST, data=serializer.data)


friend_requests_list_create_view = FriendRequestsListCreateView.as_view()
friend_requests_receive_list_view = FriendRequestsReceiveListView.as_view()
friend_request_view = FriendRequestView.as_view()
