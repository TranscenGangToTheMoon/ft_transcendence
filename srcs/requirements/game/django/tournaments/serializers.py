from math import log2
from threading import Thread

from django.db.models.functions import Random
from rest_framework import serializers

from lib_transcendence.serializer import Serializer
from lib_transcendence.sse_events import create_sse_event, EventCode
from lib_transcendence.users import retrieve_users
from matches.models import Matches
from matches.serializers import TournamentMatchSerializer
from tournaments.models import Tournaments


class TournamentPlayerSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    trophies = serializers.IntegerField()

# todo guest pp
# todo fix pp order
class TournamentSerializer(Serializer):
    id = serializers.IntegerField()
    matches = serializers.SerializerMethodField(read_only=True)
    participants = serializers.ListField(child=TournamentPlayerSerializer(), write_only=True)

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
            'participants',
        ]
        read_only_fields = [
            'start_at',
            'finish_at',
        ]

    def get_matches(self, obj):
        matches = {}
        users = []
        for match in Matches.objects.filter(tournament_id=obj.id):
            for player in match.players.all():
                if player.user_id not in users:
                    users.append(player.user_id)
        if self.context.get('retrieve_users', True):
            context = {'users': retrieve_users(users, return_type=dict)}
        else:
            context = {'retrieve_users': False}
        for stage in obj.stages.all():
            result = TournamentMatchSerializer(Matches.objects.filter(tournament_stage_id=stage.id).order_by('tournament_n'), many=True, context=context).data
            matches[stage.label] = result
        return matches

    def create(self, validated_data):
        participants = validated_data.pop('participants')
        result = super().create(validated_data)
        for user in participants:
            result.players.create(user_id=user['id'], trophies=user['trophies'])
        for n_stage in range(int(log2(result.size))):
            result.stages.create(label=Tournaments.stage_labels[n_stage], stage=n_stage)
        result.current_stage = result.stages.last()
        result.save()
        first_stage = result.current_stage
        players = result.players.all().order_by('-trophies', Random())

        for n, p in enumerate(players):
            p.seed = n + 1
            p.stage = first_stage
            p.save()

        for i in range(int(result.size / 2)):
            user_1 = players[i]
            index = result.match_order[result.size][user_1.seed]
            user_1.index = index
            user_1.save()
            k = result.size - i - 1
            if players.count() > k:
                user_2 = players[k]
                user_2.index = index
                user_2.save()
            else:
                user_2 = None
            result.create_match(index, first_stage, user_1, user_2)
            result.nb_matches = index
        result.save()
        create_sse_event(result.users_id(), EventCode.TOURNAMENT_START, TournamentSerializer(result).data, {'name': result.name})
        Thread(target=result.post_matches, args=(first_stage, True)).start()
        Thread(target=result.main_thread).start()
        return result
