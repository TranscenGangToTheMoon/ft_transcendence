from django.db.models import Q
from rest_framework import generics
from rest_framework.exceptions import NotAuthenticated, NotFound, APIException

from friends.models import Friends
from friends.utils import get_friend
from lib_transcendence import endpoints
from lib_transcendence.exceptions import MessagesException
from lib_transcendence.permissions import GuestCannotDestroy
from lib_transcendence.services import request_matchmaking, request_chat
from lib_transcendence.sse_events import EventCode
from sse.events import publish_event
from users.auth import auth_delete, get_valid_user, get_user
from users.models import Users
from users.permissions import NotInGame
from users.serializers import UsersSerializer, UsersMeSerializer, ManageUserSerializer, AuthMatchmakingSerializer
from users.serializers_utils import SmallUsersSerializer, LargeUsersSerializer


class UsersMeView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UsersMeSerializer
    permission_classes = [GuestCannotDestroy, NotInGame]

    def get_object(self):
        try:
            return Users.objects.get(id=self.request.user.id)
        except Users.DoesNotExist:
            raise NotFound(MessagesException.NotFound.USER)

    def destroy(self, request, *args, **kwargs):
        password = self.request.data.get('password')
        if password is None:
            raise NotAuthenticated({'password': MessagesException.Authentication.PASSWORD_CONFIRMATION_REQUIRED})

        auth_delete(self.request.headers.get('Authorization'), {'password': password})

        user = self.get_object()
        for friendship in Friends.objects.filter(Q(user_1=user) | Q(user_2=user)):
            publish_event(get_friend(friendship, user), EventCode.DELETE_FRIEND, {'id': friendship.id})

        for friend_request_received in user.friend_requests_received.all():
            publish_event(friend_request_received.sender, EventCode.REJECT_FRIEND_REQUEST, {'id': friend_request_received.id})

        for friend_request_sent in user.friend_requests_sent.all():
            publish_event(friend_request_sent.receiver, EventCode.CANCEL_FRIEND_REQUEST, {'id': friend_request_sent.id})

        endpoint = endpoints.UsersManagement.fdelete_user.format(user_id=user.id)
        try:
            request_matchmaking(endpoint, 'DELETE')
        except APIException:
            pass

        try:
            request_chat(endpoint, 'DELETE')
        except APIException:
            pass

        publish_event(user, EventCode.DELETE_USER)
        return super().destroy(request, *args, **kwargs)


class RetrieveUserView(generics.RetrieveAPIView):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer

    def get_object(self):
        return get_valid_user(get_user(self.request), False, True, id=self.kwargs['user_id'])


class RetrieveUsersView(generics.ListAPIView):
    pagination_class = None
    authentication_classes = []

    def get_serializer_class(self):
        size = self.request.data.get('size')
        if size == 'large':
            return LargeUsersSerializer
        return SmallUsersSerializer

    def get_queryset(self):
        user_ids = self.request.data.get('user_ids')
        if isinstance(user_ids, list):
            return Users.objects.filter(id__in=user_ids)


class ManageUserView(generics.CreateAPIView, generics.UpdateAPIView):
    serializer_class = ManageUserSerializer
    authentication_classes = []

    def get_object(self):
        return get_user(id=self.request.data.get('id'))


class AuthMatchmakingView(generics.RetrieveAPIView):
    serializer_class = AuthMatchmakingSerializer

    def get_object(self):
        return get_user(self.request)


users_me_view = UsersMeView.as_view()
retrieve_user_view = RetrieveUserView.as_view()
retrieve_users_view = RetrieveUsersView.as_view()
manage_user_view = ManageUserView.as_view()
auth_matchmaking_view = AuthMatchmakingView.as_view()
