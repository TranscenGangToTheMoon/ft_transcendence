from lib_transcendence.exceptions import MessagesException
from lib_transcendence.serializer import SerializerKwargsContext
from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView

from chats.models import Chats
from user_management.models import Users
from user_management.serializers import BlockChatSerializer, UserDataSerializer
from chats.utils import get_chat_together
from user_management.serializers import UserSerializer


class UserMixin(APIView):
    authentication_classes = []

    def get_object(self):
        try:
            return Users.objects.get(id=self.kwargs['user_id'])
        except Users.DoesNotExist:
            raise NotFound(MessagesException.NotFound.USER)


class DownloadDataView(SerializerKwargsContext, generics.ListAPIView):
    queryset = Chats.objects.all()
    serializer_class = UserDataSerializer
    authentication_classes = []
    pagination_class = None

    def filter_queryset(self, queryset):
        return Chats.objects.filter(participants__user__id=self.kwargs['user_id'])

    def get_serializer_context(self):
        return {'auth_user': {'id': self.kwargs['user_id']}, 'user_id': self.kwargs['user_id']}


class RenameUserView(UserMixin, generics.UpdateAPIView):
    serializer_class = UserSerializer


class UpdateBlockedUserView(UserMixin, generics.UpdateAPIView):
    serializer_class = BlockChatSerializer

    def get_object(self):
        return get_chat_together(self.kwargs['user_id'], self.kwargs['blocked_user_id'], field='user__id', raise_exception=True)


class DeleteUserView(UserMixin, generics.DestroyAPIView):

    def delete(self, request, *args, **kwargs):
        Chats.objects.filter(participants__user__id=kwargs['user_id']).delete()
        return super().delete(request, *args, **kwargs)


export_data_view = DownloadDataView.as_view()
rename_user_view = RenameUserView.as_view()
blocked_user_view = UpdateBlockedUserView.as_view()
delete_user_view = DeleteUserView.as_view()
