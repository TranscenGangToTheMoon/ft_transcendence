from rest_framework import generics
from rest_framework.exceptions import NotAuthenticated, NotFound, APIException
from lib_transcendence.exceptions import MessagesException
from lib_transcendence import endpoints
from lib_transcendence.services import request_matchmaking, request_chat
from lib_transcendence.sse_events import EventCode

from friends.models import Friends
from sse.events import publish_event
from users.auth import auth_delete, get_valid_user, get_user
from users.models import Users
from users.serializers import UsersSerializer, UsersMeSerializer, ManageUserSerializer


class UsersMeView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UsersMeSerializer

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
        friendships = Friends.objects.filter(friends__id=user.id)
        for friendship in friendships:
            other_user = friendship.friends.exclude(id=user.id).first()
            publish_event(other_user, EventCode.DELETE_FRIEND, {'id': friendship.id})
        friendships.delete()

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
    serializer_class = UsersSerializer
    pagination_class = None
    authentication_classes = []

    def get_queryset(self):
        user_ids = self.request.data.get('user_ids')
        if isinstance(user_ids, list):
            return Users.objects.filter(id__in=user_ids)


class ManageUserView(generics.CreateAPIView, generics.UpdateAPIView):
    serializer_class = ManageUserSerializer
    authentication_classes = []

    def get_object(self):
        return get_user(id=self.request.data.get('id'))


users_me_view = UsersMeView.as_view()
retrieve_user_view = RetrieveUserView.as_view()
retrieve_users_view = RetrieveUsersView.as_view()
manage_user_view = ManageUserView.as_view()
