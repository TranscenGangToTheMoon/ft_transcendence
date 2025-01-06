from lib_transcendence.users import retrieve_users
from rest_framework import serializers

from matches.models import Matches
from matches.serializers import MatchSerializer
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
            'created_at',
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
        context = retrieve_users(users)
        for stage in obj.stages.all():
            result = MatchSerializer(stage.matches.all().order_by('n'), many=True, context={'users': context}).data
            matches[stage.label] = result
        return matches

    def create(self, validated_data): # todo continue to fix that
        print('VALIDATAE', validated_data, flush=True)
        stages = validated_data.pop('stages')
        result = super().create(validated_data)
        for stage in stages:
            result.stages.create(**stage)
        return result
