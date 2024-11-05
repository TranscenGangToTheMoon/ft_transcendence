from lib_transcendence.GameMode import GameMode
from lib_transcendence.Lobby import MatchType, Teams
from lib_transcendence.auth import get_auth_user
from lib_transcendence.utils import generate_code
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, NotFound

from lobby.models import Lobby, LobbyParticipants
from matchmaking.utils import verify_user, can_join, get_lobby


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

        if instance.lobby.game_mode != GameMode.custom_game:
            representation.pop('team', None)
        return representation


class LobbySerializer(serializers.ModelSerializer):
    participants = LobbyGetParticipantsSerializer(many=True, read_only=True)
    is_full = serializers.BooleanField(read_only=True)

    class Meta:
        model = Lobby
        fields = '__all__'
        read_only_fields = [
            'code',
            'max_participants',
            'created_at',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.instance:
            self.fields['match_type'].read_only = True

    @staticmethod
    def get_is_full(obj):
        return obj.is_full

    @staticmethod
    def validate_game_mode(value):
        return GameMode.validate_lobby(value)

    @staticmethod
    def validate_match_type(value):
        return MatchType.validate(value)

    @staticmethod
    def validate_bo(value):
        if value not in (1, 3, 5):
            raise serializers.ValidationError(['BO must be 1, 3 or 5.'])
        return value

    def create(self, validated_data):
        user = get_auth_user(self.context.get('request'))

        if user['is_guest']:
            raise PermissionDenied('Guest cannot create lobby.')

        verify_user(user['id'])

        validated_data['code'] = generate_code(Lobby)
        if validated_data['game_mode'] == GameMode.clash:
            validated_data['match_type'] = MatchType.m3v3
            validated_data['max_participants'] = 3
        else:
            validated_data['match_type'] = MatchType.m1v1
            validated_data['max_participants'] = 6
        result = super().create(validated_data)
        creator = LobbyParticipants.objects.create(lobby_id=result.id, lobby_code=validated_data['code'], user_id=user['id'], creator=True)
        if validated_data['game_mode'] == GameMode.custom_game:
            creator.team = Teams.a
            creator.save()
        return result

    def update(self, instance, validated_data):
        if 'game_mode' in validated_data:
            raise PermissionDenied({'game_mode': ['You cannot update game mode.']})
        if validated_data.get('match_type') == MatchType.m1v1 and instance.match_type == MatchType.m3v3:
            participants = instance.participants

            for team in Teams.play:
                for p in participants.filter(team=team)[1:]:
                    p.team = Teams.spectator
                    p.save()

        return super().update(instance, validated_data)


class LobbyParticipantsSerializer(serializers.ModelSerializer):
    creator = serializers.BooleanField(read_only=True)
    id = serializers.IntegerField(source='user_id', read_only=True)

    class Meta:
        model = LobbyParticipants
        fields = [
            'id',
            'lobby_code',
            'team',
            'is_ready',
            'creator',
            'join_at',
        ]
        read_only_fields = [
            'id',
            'lobby_code',
            'creator',
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.lobby.game_mode != GameMode.custom_game:
            representation.pop('team', None)
        return representation

    @staticmethod
    def validate_team(value):
        return Teams.validate(value)

    def create(self, validated_data):
        lobby = get_lobby(self.context.get('code'), True)
        user = get_auth_user(self.context.get('request'))

        if lobby.participants.filter(user_id=user['id']).exists():
            raise PermissionDenied('You already joined this lobby.')

        if not can_join(self.context.get('request'), lobby, user['id']):
            raise NotFound({'code': ['Lobby code does not exist.']}) # todo move to library

        verify_user(user['id'])

        if lobby.is_full:
            raise PermissionDenied('Lobby is full.')

        validated_data['lobby'] = lobby
        validated_data['lobby_code'] = lobby.code
        validated_data['user_id'] = user['id']
        validated_data['is_guest'] = user['is_guest']
        if lobby.game_mode == GameMode.custom_game:
            for t in Teams.all:
                if not lobby.is_team_full(t):
                    validated_data['team'] = t
                    break
        return super().create(validated_data)
        #todo websocket: send to chat that user 'xxx' join team

    def update(self, instance, validated_data):
        if 'team' in validated_data:
            if instance.lobby.game_mode != GameMode.custom_game:
                raise PermissionDenied(f'You cannot update team in {GameMode.clash} mode.')
            elif instance.team == validated_data['team']:
                raise PermissionDenied('You are already in this team.')
            elif self.instance.lobby.is_team_full(validated_data['team']):
                raise PermissionDenied('Team is full.')
        result = super().update(instance, validated_data)
        # todo websocket: send that lobby thas x change team
        if instance.lobby.is_ready:
            # todo websocket: send that lobby is ready and start game
            pass
        return result
