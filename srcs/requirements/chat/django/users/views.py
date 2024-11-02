from rest_framework import generics, status, serializers
from rest_framework.response import Response

from chats.models import ChatParticipants, Chats
from chats.serializers import BlockChatSerializer
from chats.utils import get_chat_together


#todo try to make with generics view
class RenameUserView(generics.UpdateAPIView):
    def update(self, request, *args, **kwargs):
        new_username = request.data.get('username')
        if not new_username:
            raise serializers.ValidationError({'username': ['This field is required.']})
        players_queryset = ChatParticipants.objects.filter(user_id=kwargs['user_id'])
        updated_count = players_queryset.update(username=new_username)

        return Response(
            {'message': f'{updated_count} players updated successfully'},
            status=status.HTTP_200_OK
        )


class UpdateBlockUserView(generics.UpdateAPIView):
    serializers = BlockChatSerializer

    def get_object(self): #todo test si ca marche
        return get_chat_together(self.kwargs['user_id'], self.kwargs['user_block'])


class DeleteUserView(generics.DestroyAPIView):
    def delete(self, request, *args, **kwargs):
        chats = ChatParticipants.objects.filter(user_id=kwargs['user_id']).values_list('chat', flat=True)
        Chats.objects.filter(id__in=chats).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


rename_user_view = RenameUserView.as_view()
block_user_view = UpdateBlockUserView.as_view()
delete_user_view = DeleteUserView.as_view()
