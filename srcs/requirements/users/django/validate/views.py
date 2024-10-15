from rest_framework import generics, serializers

from block.models import Block
from friends.exist import is_friendship
from users.models import Users
from users.serializers import UsersSerializer


class ValidateChatView(generics.RetrieveAPIView):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    lookup_field = 'username'

    def get_object(self):
        try:
            username = self.request.data.get('username')
            print(username, flush=True)
            assert username is not None
            print('1', flush=True)
            valide_user = Users.objects.get(username=username)
            print('2', flush=True)
            assert valide_user.is_guest is False
            print('3', flush=True)
            assert not Block.objects.filter(user=valide_user, blocked=self.request.user.id).exists()
            print('4', flush=True)
        except (Users.DoesNotExist, AssertionError):
            raise serializers.ValidationError({'username': ['This user does not exist.']})
        if valide_user.accept_chat_state & (2 + int(is_friendship(valide_user.id, self.request.user.id))):
            return valide_user
        raise serializers.ValidationError({'username': ['This user does not accept chat.']})


validate_chat_view = ValidateChatView.as_view()
