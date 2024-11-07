from lib_transcendence.Chat import AcceptChat
from lib_transcendence.exceptions import MessagesException
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied, NotFound

from block.models import Blocks
from block.serializers import BlockSerializer
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
        username2 = get_user(id=self.kwargs['username2'])

        if user1.block.filter(blocked__username=username2).exists():
            raise PermissionDenied(MessagesException.PermissionDenied.BLOCK_USER)

        valide_user = get_valid_user(user1, username2)
        if AcceptChat.is_accept(valide_user.accept_chat_from, is_friendship(valide_user.id, self.request.user.id)):
            return valide_user
        raise PermissionDenied(MessagesException.PermissionDenied.NOT_ACCEPT_CHAT)


class ValidateBlockView(generics.RetrieveAPIView):
    queryset = Blocks.objects.all()
    serializer_class = BlockSerializer
    permission_classes = []

    def get_object(self):
        user1 = get_user(id=self.kwargs['user1_id'])
        user2 = get_user(id=self.kwargs['user2_id'])
        try:
            return user1.block.get(blocked=user2)
        except Blocks.DoesNotExist:
            pass
        try:
            return user2.block.get(blocked=user1)
        except Blocks.DoesNotExist:
            pass
        raise NotFound()


validate_chat_view = ValidateChatView.as_view()
validate_block_view = ValidateBlockView.as_view()
