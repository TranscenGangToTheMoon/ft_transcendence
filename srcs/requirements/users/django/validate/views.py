from lib_transcendence.Chat import AcceptChat
from lib_transcendence.exceptions import MessagesException
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied, NotFound

from blocking.models import BlockedUsers
from blocking.serializers import BlockedSerializer
from friends.utils import is_friendship
from users.auth import get_user, get_valid_user
from users.models import Users
from users.serializers import UsersSerializer


class ValidateChatView(generics.RetrieveAPIView):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    permission_classes = []

    def get_object(self):
        user1 = get_user(id=self.kwargs['user1_id'])

        if user1.blocked.filter(blocked__username=self.kwargs['username2']).exists():
            raise PermissionDenied(MessagesException.PermissionDenied.BLOCK_USER)

        valide_user = get_valid_user(user1, self.kwargs['username2'])
        if AcceptChat.is_accept(valide_user.accept_chat_from, is_friendship(valide_user.id, user1.id)):
            return valide_user
        raise PermissionDenied(MessagesException.PermissionDenied.NOT_ACCEPT_CHAT)


class AreBlockedView(generics.RetrieveAPIView):
    queryset = BlockedUsers.objects.all()
    serializer_class = BlockedSerializer
    permission_classes = []

    def get_object(self):
        user1 = get_user(id=self.kwargs['user1_id'])
        user2 = get_user(id=self.kwargs['user2_id'])
        try:
            return user1.blocked.get(blocked=user2)
        except BlockedUsers.DoesNotExist:
            pass
        try:
            return user2.blocked.get(blocked=user1)
        except BlockedUsers.DoesNotExist:
            pass
        raise NotFound()


validate_chat_view = ValidateChatView.as_view()
are_blocked_view = AreBlockedView.as_view()
