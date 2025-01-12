from lib_transcendence.chat import AcceptChat
from lib_transcendence.exceptions import MessagesException
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied, NotFound

from friends.models import Friends
from friends.serializers import FriendsSerializer
from friends.utils import is_friendship, get_friendship
from users.auth import get_user, get_valid_user
from users.models import Users
from users.serializers import UsersSerializer


class ValidateChatView(generics.RetrieveAPIView):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    authentication_classes = []

    def get_object(self):
        user1 = get_user(id=self.kwargs['user1_id'])

        valide_user = get_valid_user(user1, self_blocked=True, username=self.kwargs['username2'])
        if AcceptChat.is_accept(valide_user.accept_chat_from, is_friendship(valide_user.id, user1.id)):
            return valide_user
        raise PermissionDenied(MessagesException.PermissionDenied.NOT_ACCEPT_CHAT)


class AreFriendsView(generics.RetrieveAPIView):
    queryset = Friends.objects.all()
    serializer_class = FriendsSerializer
    authentication_classes = []

    def get_object(self):
        user1 = get_user(id=self.kwargs['user1_id'])
        user2 = get_user(id=self.kwargs['user2_id'])
        friendship = get_friendship(user1, user2)
        if friendship is None:
            raise NotFound(MessagesException.NotFound.FRIENDSHIP)
        return friendship


validate_chat_view = ValidateChatView.as_view()
are_friends_view = AreFriendsView.as_view()
