from rest_framework.exceptions import NotFound

from baning.utils import banned
from blocking.models import Blocked
from lib_transcendence.exceptions import MessagesException
from lib_transcendence.serializer import Serializer
from lobby.models import LobbyParticipants
from matchmaking.model import ParticipantsPlace
from play.models import Players
from tournament.models import TournamentParticipants


class BlockedSerializer(Serializer):
    class Meta:
        model = Blocked
        fields = '__all__'
        read_only_fields = [
            'user_id',
            'blocked_user_id'
        ]

    def validate(self, attrs):
        attrs['user_id'] = self.context.get('user_id')
        attrs['blocked_user_id'] = self.context.get('blocked_user_id')
        return attrs

    def create(self, validated_data):
        model: ParticipantsPlace

        for model in (LobbyParticipants, TournamentParticipants, Players):
            user = get_user_from_model(validated_data['user_id'], model)
            if user is not None:
                break

        if user is None:
            raise NotFound(MessagesException.NotFound.USER)

        if not isinstance(model, Players):
            blocked_user = get_user_from_model(validated_data['blocked_user_id'], model)
            if blocked_user is not None:
                if user.place.id == blocked_user.place.id:
                    if user.creator:
                        banned(blocked_user, False)
                        blocked_user.delete()
                    elif blocked_user.creator:
                        banned(user, False)
                        user.delete()

        return super().create(validated_data)


def get_user_from_model(user_id, model: ParticipantsPlace):
    try:
        return model.objects.get(user_id=user_id)
    except model.DoesNotExist:
        pass
