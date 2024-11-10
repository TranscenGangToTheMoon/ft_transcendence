from rest_framework import generics, status
from rest_framework.response import Response

from lobby.models import LobbyParticipants
from play.models import Players
from tournament.models import TournamentParticipants


class BlockUserView(generics.DestroyAPIView):
    permission_classes = []

    def destroy(self, request, *args, **kwargs):
        self.kick_blocked_user_or_leave(LobbyParticipants)
        self.kick_blocked_user_or_leave(TournamentParticipants)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def kick_blocked_user_or_leave(self, model):
        def get_user(user_id):
            try:
                return model.objects.get(user_id=user_id)
            except model.DoesNotExist:
                return None

        user = get_user(self.kwargs['user_id'])
        if user is None:
            return

        blocked_user = get_user(self.kwargs['blocked_user_id'])
        if blocked_user is None:
            return

        if user.get_location_id() == block_user.get_location_id():
            if user.creator:
                block_user.delete()
            else:
                user.delete()


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


blocked_user_view = BlockUserView.as_view()
delete_user_view = DeleteUserView.as_view()
