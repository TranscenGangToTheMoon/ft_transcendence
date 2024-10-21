from rest_framework import serializers

from lobby.static import match_type_1v1, match_type_3v3, team_a, team_b, team_spectator, lobby_clash, lobby_custom_game
from matchmaking.auth import get_auth_user, generate_lobby_code
from lobby.models import Lobby, LobbyParticipants


# todo add option for kick people
class LobbySerializer(serializers.ModelSerializer):

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

    def validate_game_mode(self, value):
        if value not in (lobby_clash, lobby_custom_game):
            raise serializers.ValidationError([f"Game mode must be '{lobby_clash}' or '{lobby_custom_game}'."])
        return value

    def validate_match_type(self, value):
        if value not in (match_type_1v1, match_type_3v3):
            raise serializers.ValidationError([f"Match type must be '{match_type_1v1}' or '{match_type_3v3}'."])
        return value

    def validate_bo(self, value):
        if value not in (1, 3, 5):
            raise serializers.ValidationError(['BO must be 1, 3 or 5.'])
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        user = get_auth_user(request)

        if user['is_guest']:
            raise serializers.ValidationError({'detail': 'Guest cannot create lobby.'})

        LobbyParticipants.objects.filter(user_id=user['id']).delete()

        validated_data['code'] = generate_lobby_code()
        if validated_data['game_mode'] == lobby_clash:
            validated_data['match_type'] = match_type_3v3
            validated_data['max_participants'] = 3
        else:
            validated_data['match_type'] = match_type_1v1
            validated_data['max_participants'] = 6
        result = super().create(validated_data)
        LobbyParticipants.objects.create(lobby_id=result.id, lobby_code=validated_data['code'], user_id=user['id'], username=user['username'], is_admin=True)
        return result

    def update(self, instance, validated_data):
        if 'game_mode' in validated_data:
            raise serializers.ValidationError({'game_mode': ['You cannot update game mode.']})
        if validated_data.get('match_type') == match_type_1v1 and instance.match_type == match_type_3v3:
            participants = instance.participants

            for team in (team_a, team_b):
                for p in participants.filter(team=team)[1:]:
                    p.team = team_spectator
                    p.save()

        return super().update(instance, validated_data)


class LobbyParticipantsSerializer(serializers.ModelSerializer):
    is_admin = serializers.BooleanField(read_only=True)

    class Meta:
        model = LobbyParticipants
        fields = '__all__'
        read_only_fields = [
            'lobby',
            'lobby_code',
            'user_id',
            'username',
            'is_admin',
        ]

    def validate_team(self, value):
        if value not in (team_a, team_b, team_spectator):
            raise serializers.ValidationError([f"Team must be '{team_a}', '{team_b}' or '{team_spectator}'."])
        return value

    def create(self, validated_data):
        lobby_code = self.context.get('code')
        if lobby_code is None:
            raise serializers.ValidationError({'detail': 'Lobby code is required.'})

        try:
            lobby = Lobby.objects.get(code=lobby_code)
        except Lobby.DoesNotExist:
            raise serializers.ValidationError({'code': [f"Lobby '{lobby_code}' does not exist."]})

        user = self.context['auth_user']
        lobby_join = LobbyParticipants.objects.filter(user_id=user['id'])
        if lobby_join.filter(lobby_id=lobby.id).exists():
            raise serializers.ValidationError({'code': ['You already joined this lobby.']})

        if lobby_join.exists():
            lobby_join.delete()

        if lobby.is_full:
            raise serializers.ValidationError({'code': ['Lobby is full.']})

        validated_data['lobby_id'] = lobby.id
        validated_data['lobby_code'] = lobby.code
        validated_data['user_id'] = user['id']
        validated_data['username'] = user['username']

        if lobby.game_mode == lobby_custom_game:
            teams_count = lobby.teams_count
            max_team = lobby.max_team_participants

            if teams_count[team_a] < max_team:
                validated_data['team'] = team_a
            elif teams_count[team_b] < max_team:
                validated_data['team'] = team_b
            else:
                validated_data['team'] = team_spectator
        return super().create(validated_data) #todo: send to chat that user xxx join team

    def update(self, instance, validated_data):
        if 'team' in validated_data:
            if self.instance.lobby.teams_count[validated_data['team']] == self.instance.lobby.max_team_participants:
                raise serializers.ValidationError({'team': [f"Team {validated_data['team']} is full."]})
        # todo : if all user are ready, play game
        return super().update(instance, validated_data)
