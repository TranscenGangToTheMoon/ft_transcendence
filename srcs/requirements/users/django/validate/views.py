from lib_transcendence.Chat import AcceptChat
from rest_framework import generics, serializers

from friends.utils import is_friendship
from users.auth import validate_username, get_user
from users.models import Users
from users.serializers import UsersSerializer


class ValidateChatView(generics.RetrieveAPIView):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer

    def get_object(self):
        self_user = get_user(self.request)
        test_username = self.request.data.get('username')
        if not test_username:
            raise serializers.ValidationError({'username': ['This field is required.']})
        if self_user.block.filter(blocked__username=test_username).exists():
            raise serializers.ValidationError({'username': ['You block this user.']})
        valide_user = validate_username(test_username, self_user)
        if AcceptChat.is_accept(valide_user.accept_chat_from, is_friendship(valide_user.id, self.request.user.id)):
            return valide_user
        raise serializers.ValidationError({'username': ['This user does not accept new chat.']})


validate_chat_view = ValidateChatView.as_view()
