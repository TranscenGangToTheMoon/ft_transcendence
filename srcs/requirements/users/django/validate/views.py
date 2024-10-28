from rest_framework import generics, serializers

from friends.exist import is_friendship
from users.auth import validate_username, get_user
from users.models import Users
from users.serializers import UsersSerializer


class ValidateChatView(generics.RetrieveAPIView):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    lookup_field = 'username'

    def get_object(self):
        valide_user = validate_username(self.request.data.get('username'), get_user(self.request))
        if valide_user.accept_chat_state & (2 + int(is_friendship(valide_user.id, self.request.user.id))):
            return valide_user
        raise serializers.ValidationError({'username': ['This user does not accept chat.']})


validate_chat_view = ValidateChatView.as_view()
