from lib_transcendence.exceptions import MessagesException
from rest_framework import generics, status, serializers
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from chats.models import ChatParticipants, Chats
from chats.serializers import BlockChatSerializer
from chats.utils import get_chat_together


#todo try to make with generics view
class RenameUserView(generics.UpdateAPIView):
    def update(self, request, *args, **kwargs):
        new_username = request.data.get('username')
        if not new_username:
            raise serializers.ValidationError({'username': [MessagesException.ValidationError.FIELD_REQUIRED]})
        players_queryset = ChatParticipants.objects.filter(user_id=kwargs['user_id'])
        updated_count = players_queryset.update(username=new_username)

        return Response(
            {'message': f'{updated_count} players updated successfully'},
            status=status.HTTP_200_OK
        )


class UpdateBlockedUserView(generics.UpdateAPIView):
    serializer_class = BlockChatSerializer
    permission_classes = []

    def update(self, request, *args, **kwargs):
        if self.get_object() is None:
            raise NotFound()
        return super().update(request, *args, **kwargs)

    def get_object(self):
        return get_chat_together(self.kwargs['user_id'], self.kwargs['blocked_user_id'], field='user_id')


class DeleteUserView(generics.DestroyAPIView):
    def delete(self, request, *args, **kwargs):
        chats = ChatParticipants.objects.filter(user_id=kwargs['user_id']).values_list('chat', flat=True)
        Chats.objects.filter(id__in=chats).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


rename_user_view = RenameUserView.as_view()
blocked_user_view = UpdateBlockedUserView.as_view()
delete_user_view = DeleteUserView.as_view()
