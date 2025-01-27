from django.db.models import Q
from lib_transcendence.exceptions import MessagesException
from lib_transcendence.permissions import NotGuest
from lib_transcendence.serializer import SerializerKwargsContext
from lib_transcendence.sse_events import EventCode
from rest_framework import generics
from rest_framework.exceptions import NotFound

from friend_requests.models import FriendRequests
from friend_requests.serializers import FriendRequestsSerializer
from friends.serializers import FriendsSerializer
from profile_pictures.unlock import unlock_friends_pp
from sse.events import publish_event


class FriendRequestsMixin(generics.GenericAPIView):
    queryset = FriendRequests.objects.all()
    serializer_class = FriendRequestsSerializer
    permission_classes = [NotGuest]


class FriendRequestsListCreateView(generics.ListCreateAPIView, FriendRequestsMixin):

    def filter_queryset(self, queryset):
        return queryset.filter(sender=self.request.user.id)

    def perform_create(self, serializer):
        super().perform_create(serializer)
        publish_event(serializer.instance.receiver, EventCode.RECEIVE_FRIEND_REQUEST, data=serializer.data, kwargs={'username': serializer.data['sender']['username']})


class FriendRequestsReceiveListView(generics.ListAPIView, FriendRequestsMixin):

    def filter_queryset(self, queryset):
        return queryset.filter(receiver=self.request.user.id)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        self.filter_queryset(self.get_queryset()).update(new=False)
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
        publish_event(serializer.instance.user_1, EventCode.ACCEPT_FRIEND_REQUEST, data=serializer.data, kwargs={'username': serializer.instance.user_2.username})
        unlock_friends_pp(serializer.instance)

    def perform_destroy(self, instance):
        user_id = self.request.user.id
        if instance.sender.id == user_id:
            code = EventCode.CANCEL_FRIEND_REQUEST
            sse_user = instance.receiver
        else:
            code = EventCode.REJECT_FRIEND_REQUEST
            sse_user = instance.sender
        publish_event(sse_user, code, data={'id': instance.id})
        super().perform_destroy(instance)


friend_requests_list_create_view = FriendRequestsListCreateView.as_view()
friend_requests_receive_list_view = FriendRequestsReceiveListView.as_view()
friend_request_view = FriendRequestView.as_view()
