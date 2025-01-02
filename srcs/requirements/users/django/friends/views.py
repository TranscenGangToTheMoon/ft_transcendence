from django.db.models import Q
from lib_transcendence.permissions import NotGuest
from lib_transcendence.sse_events import EventCode
from lib_transcendence.exceptions import MessagesException
from rest_framework import generics
from rest_framework.exceptions import NotFound

from friends.models import Friends
from friends.serializers import FriendsSerializer
from friends.utils import get_friend
from sse.events import publish_event


class FriendsMixin(generics.GenericAPIView):
    queryset = Friends.objects.all()
    serializer_class = FriendsSerializer
    permission_classes = [NotGuest]


class FriendsView(generics.ListAPIView, FriendsMixin):
    def filter_queryset(self, queryset):
        kwargs1 = {'user_1': self.request.user.id}
        kwargs2 = {'user_2': self.request.user.id}
        online = self.request.query_params.get('online')
        if online in ('true', 'false'):
            kwargs1['user_2__is_online'] = online == 'true'
            kwargs2['user_1__is_online'] = online == 'true'
        return queryset.filter(Q(**kwargs1) | Q(**kwargs2))


class FriendView(generics.RetrieveDestroyAPIView, FriendsMixin):

    def get_object(self):
        try:
            return self.queryset.get(Q(user_1=self.request.user.id) | Q(user_2=self.request.user.id), id=self.kwargs['friendship_id'])
        except Friends.DoesNotExist:
            raise NotFound(MessagesException.NotFound.FRIENDSHIP)

    def perform_destroy(self, instance):
        publish_event(get_friend(instance, self.request.user), EventCode.DELETE_FRIEND, data={'id': instance.id})
        super().perform_destroy(instance)


friends_view = FriendsView.as_view()
friend_view = FriendView.as_view()
