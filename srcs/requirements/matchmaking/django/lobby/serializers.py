from lib_transcendence.exceptions import MessagesException, ResourceExists
from lib_transcendence.game import GameMode
from lib_transcendence.lobby import MatchType, Teams
from lib_transcendence.auth import get_auth_user
from lib_transcendence.generate import generate_code
from lib_transcendence.sse_events import EventCode, create_sse_event
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from blocking.utils import create_player_instance
from lobby.models import Lobby, LobbyParticipants
from matchmaking.utils.participant import get_participants
from matchmaking.utils.place import get_lobby, verify_place
from matchmaking.utils.sse import send_sse_event
from matchmaking.utils.user import verify_user


class LobbyGetParticipantsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='user_id')

    class Meta:
        model = LobbyParticipants
        fields = [
            'id',
            'team',
            'creator',
            'join_at',
            'is_ready',
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.lobby.game_mode != GameMode.CUSTOM_GAME:
            representation.pop('team', None)
        return representation


class LobbySerializer(serializers.ModelSerializer):
    participants = serializers.SerializerMethodField(read_only=True)
    match_type = serializers.CharField(max_length=3, required=False)

    class Meta:
        model = Lobby
        fields = [
            'id',
            'code',
            'is_ready',
            'is_playing',
            'participants',
            'max_participants',
            'created_at',
            'game_mode',
            'match_type',
        ]
        read_only_fields = [
            'id',
            'code',
            'is_ready',
            'is_playing',
            'participants',
            'max_participants',
            'created_at',
        ]

    @staticmethod
    def validate_game_mode(value):
        return GameMode.validate_lobby(value)

    @staticmethod
    def validate_match_type(value):
        return MatchType.validate(value)

    @staticmethod
    def get_participants(obj):
        fields = ['is_ready']
        if obj.game_mode == GameMode.CUSTOM_GAME:
            fields.extend(['team'])
        return get_participants(obj, fields)

    def create(self, validated_data):
        request = self.context.get('request')
        user = get_auth_user(request)

        verify_user(user['id'])

        validated_data['code'] = generate_code(Lobby)
        if validated_data['game_mode'] == GameMode.CLASH:
            validated_data['match_type'] = MatchType.M3V3
            validated_data['max_participants'] = 3
        else:
            if 'match_type' not in validated_data:
                validated_data['match_type'] = MatchType.M1V1
            validated_data['max_participants'] = 6
        result = super().create(validated_data)
        creator = create_player_instance(request, LobbyParticipants, lobby_id=result.id, user_id=user['id'], creator=True)
        if validated_data['game_mode'] == GameMode.CUSTOM_GAME:
            creator.team = Teams.A
            creator.save()
        return result

    def update(self, instance, validated_data):
        if instance.is_playing:
            raise PermissionDenied(MessagesException.PermissionDenied.LOBBY_IN_GAME)

        if 'game_mode' in validated_data:
            raise PermissionDenied(MessagesException.PermissionDenied.CANNOT_UPDATE_GAME_MODE)

        participants = instance.participants.all()
        if validated_data.get('match_type') == MatchType.M1V1 and instance.match_type == MatchType.M3V3:
            for team in [Teams.A, Teams.B]:
                for p in participants.filter(team=team)[1:]:
                    participant_data = {'team': Teams.SPECTATOR}
                    p.team = Teams.SPECTATOR
                    if p.is_ready:
                        p.is_ready = False
                        participant_data['is_ready'] = False
                    p.save()
                    send_sse_event(EventCode.LOBBY_UPDATE_PARTICIPANT, p, participant_data, exclude_myself=False)

        result = super().update(instance, validated_data)
        other_members = list(participants.exclude(user_id=self.context['auth_user']['id']).values_list('user_id', flat=True))
        if other_members:
            create_sse_event(other_members, EventCode.LOBBY_UPDATE, validated_data)
        return result


class LobbyParticipantsSerializer(serializers.ModelSerializer):
    creator = serializers.BooleanField(read_only=True)
    id = serializers.IntegerField(source='user_id', read_only=True)

    class Meta:
        model = LobbyParticipants
        fields = [
            'id',
            'team',
            'is_ready',
            'creator',
            'join_at',
        ]
        read_only_fields = [
            'id',
            'creator',
            'join_at',
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.lobby.game_mode != GameMode.CUSTOM_GAME:
            representation.pop('team', None)
        return representation

    @staticmethod
    def validate_team(value):
        return Teams.validate(value)

    def create(self, validated_data):
        user = self.context['auth_user']
        lobby = get_lobby(self.context.get('code'), True)

        verify_place(user, lobby)

        validated_data['lobby'] = lobby
        validated_data['user_id'] = user['id']
        validated_data['is_guest'] = user['is_guest']
        if lobby.game_mode == GameMode.CUSTOM_GAME:
            for t in Teams.attr():
                if not lobby.is_team_full(t):
                    validated_data['team'] = t
                    break
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if instance.lobby.is_playing:
            raise PermissionDenied(MessagesException.PermissionDenied.LOBBY_IN_GAME)

        if 'team' in validated_data:
            if instance.lobby.game_mode != GameMode.CUSTOM_GAME:
                raise PermissionDenied(MessagesException.PermissionDenied.UPDATE_TEAM_CLASH_MODE)
            elif instance.team == validated_data['team']:
                raise ResourceExists(MessagesException.ResourceExists.TEAM)
            elif self.instance.lobby.is_team_full(validated_data['team']):
                raise PermissionDenied(MessagesException.PermissionDenied.TEAM_IS_FULL)
        result = super().update(instance, validated_data)
        send_sse_event(EventCode.LOBBY_UPDATE_PARTICIPANT, result, validated_data)
        if instance.lobby.is_ready:
            instance.lobby.set_ready_to_play(True)
        elif instance.lobby.ready_to_play:
            instance.lobby.set_ready_to_play(False)
        return result
