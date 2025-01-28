from rest_framework import generics
from rest_framework.exceptions import NotFound

from blocking.models import Blocked
from blocking.serializers import BlockedSerializer
from lib_transcendence.exceptions import MessagesException
from lib_transcendence.serializer import SerializerKwargsContext


class BlockedUserView(SerializerKwargsContext, generics.CreateAPIView, generics.DestroyAPIView):
    serializer_class = BlockedSerializer
    authentication_classes = []

    def get_object(self):
        try:
            return Blocked.objects.get(user_id=self.kwargs['user_id'], blocked_user_id=self.kwargs['blocked_user_id'])
        except Blocked.DoesNotExist:
            raise NotFound(MessagesException.NotFound.BLOCKED_INSTANCE)


blocked_user_view = BlockedUserView.as_view()
