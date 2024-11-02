from rest_framework import generics, status
from rest_framework.response import Response

from chats.models import ChatParticipants, Chats


#todo try to make with generics view
class RenameUserView(generics.UpdateAPIView):
    def update(self, request, *args, **kwargs):
        new_username = request.data.get('username')
        players_queryset = ChatParticipants.objects.filter(user_id=kwargs['user_id'])
        updated_count = players_queryset.update(username=new_username)

        return Response(
            {'message': f'{updated_count} players updated successfully'},
            status=status.HTTP_200_OK
        )


class DeleteUserView(generics.DestroyAPIView):
    def delete(self, request, *args, **kwargs):
        chats = ChatParticipants.objects.filter(user_id=kwargs['user_id']).values_list('chat', flat=True)
        Chats.objects.filter(id__in=chats).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


rename_user_view = RenameUserView.as_view()
delete_user_view = DeleteUserView.as_view()
