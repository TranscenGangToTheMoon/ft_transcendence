from lib_transcendence.sse_events import EventCode
from lib_transcendence.exceptions import MessagesException
from rest_framework import generics
from rest_framework.exceptions import NotFound

from friends.models import Friends
from friends.serializers import FriendsSerializer
from sse.events import publish_event


class FriendsMixin(generics.GenericAPIView):
    queryset = Friends.objects.all()
    serializer_class = FriendsSerializer


class FriendsView(generics.ListAPIView, FriendsMixin):
    def filter_queryset(self, queryset):
        return queryset.filter(friends=self.request.user.id).order_by('-last_updated')


class FriendView(generics.RetrieveDestroyAPIView, FriendsMixin):

    def get_object(self):
        try:
            return self.queryset.get(id=self.kwargs['friendship_id'], friends=self.request.user.id)
        except Friends.DoesNotExist:
            raise NotFound(MessagesException.NotFound.FRIENDSHIP)

    def perform_destroy(self, instance):
        other_user = instance.friends.exclude(id=self.request.user.id).first()
        publish_event(other_user, EventCode.DELETE_FRIEND, data={'id': instance.id})
        super().perform_destroy(instance)


friends_view = FriendsView.as_view()
friend_view = FriendView.as_view()
