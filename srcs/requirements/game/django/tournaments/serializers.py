from lib_transcendence.users import retrieve_users
from rest_framework import serializers

from matches.models import Matches
from matches.serializers import TournamentMatchSerializer
from tournaments.models import Tournaments


class TournamentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    stages = serializers.ListField(child=serializers.DictField(), write_only=True)
    matches = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Tournaments
        fields = [
            'id',
            'name',
            'size',
            'start_at',
            'finish_at',
            'created_by',
            'matches',
            'stages',
        ]

    @staticmethod
    def get_matches(obj):
        matches = {}
        users = []
        for match in Matches.objects.filter(tournament_id=obj.id):
            for player in match.players.all():
                if player.user_id not in users:
                    users.append(player.user_id)
        context_users = {}
        for user in retrieve_users(users):
            context_users[user['id']] = user
        for stage in obj.stages.all():
            result = TournamentMatchSerializer(Matches.objects.filter(tournament_stage_id=stage.id).order_by('tournament_n'), many=True, context={'users': context_users}).data
            matches[stage.label] = result
        return matches

    def create(self, validated_data):
        stages = validated_data.pop('stages')
        result = super().create(validated_data)
        for stage in stages:
            result.stages.create(**stage)
        return result
