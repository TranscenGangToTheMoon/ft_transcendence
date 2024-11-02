from django.http import Http404
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
    serializer_class = BlockChatSerializer
    permission_classes = []

    def update(self, request, *args, **kwargs):
        try:
            self.get_object()
        except Http404:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return super().update(request, *args, **kwargs)

    def get_object(self):
        together = get_chat_together(self.kwargs['user_id'], self.kwargs['user_block'], field='user_id')
        if together is None:
            raise Http404 # serializers.ValidationError({'detail': 'Chat does not exist.'})
        return together


class DeleteUserView(generics.DestroyAPIView):
    def delete(self, request, *args, **kwargs):
        chats = ChatParticipants.objects.filter(user_id=kwargs['user_id']).values_list('chat', flat=True)
        Chats.objects.filter(id__in=chats).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


rename_user_view = RenameUserView.as_view()
block_user_view = UpdateBlockUserView.as_view()
delete_user_view = DeleteUserView.as_view()
