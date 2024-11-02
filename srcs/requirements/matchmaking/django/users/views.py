from rest_framework import generics, serializers, status
from rest_framework.response import Response

from lobby.models import LobbyParticipants
from play.models import Players
from tournament.models import TournamentParticipants, Tournaments


#todo try to make with generics view
class BlockUserView(generics.UpdateAPIView):
    def update(self, request, *args, **kwargs):
        user_block = request.data.get('user_block_id')
        if not user_block:
            raise serializers.ValidationError({'user_block_id': ['This field is required.']})

        # tryy:
        #     Tournaments.objects.get(kwargs['user_id']).delete()
        #     tournament = TournamentParticipants.objects.get(kwargs['user_id'])
        #     if
        # except TournamentParticipants.DoesNotExist:
        #     pass
        try:
            # todo tesst that
            LobbyParticipants.objects.get(kwargs['user_id']).delete()
        except LobbyParticipants.DoesNotExist:
            pass

        return Response(
            {'message': 'Remove commun participation with user blocked successfully'},
            status=status.HTTP_200_OK
        )


class DeleteUserView(generics.DestroyAPIView):
    def delete(self, request, *args, **kwargs):
        try:
            TournamentParticipants.objects.get(kwargs['user_id']).delete()
        except TournamentParticipants.DoesNotExist:
            pass
        try:
            LobbyParticipants.objects.get(kwargs['user_id']).delete()
        except LobbyParticipants.DoesNotExist:
            pass
        try:
            Players.objects.get(kwargs['user_id']).delete()
        except Players.DoesNotExist:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)


block_user_view = BlockUserView.as_view()
delete_user_view = DeleteUserView.as_view()
