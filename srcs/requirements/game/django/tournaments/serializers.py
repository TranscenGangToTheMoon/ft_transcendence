from rest_framework import serializers

from lib_transcendence.serializer import Serializer
from lib_transcendence.users import retrieve_users
from matches.models import Matches
from matches.serializers import TournamentMatchSerializer
from tournaments.models import Tournaments


class TournamentSerializer(Serializer):
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
        stages = validated_data.pop('stages')
        result = super().create(validated_data)
        for stage in stages:
            result.stages.create(**stage)
        self.is_started = True
        self.start_at = datetime.now(timezone.utc)
        for n_stage in range(int(log2(self.size))):
            self.stages.create(label=Tournament.stage_labels[n_stage], stage=n_stage)
        self.current_stage = self.stages.last()
        self.save()
        first_stage = self.current_stage
        participants = self.participants.all().order_by('-trophies', Random())

        for n, p in enumerate(participants):
            p.seed = n + 1
            p.stage = first_stage
            p.save()

        for i in range(int(self.size / 2)):
            user_1 = participants[i]
            index = self.match_order[self.size][user_1.seed]
            user_1.index = index
            user_1.save()
            k = self.size - i - 1
            if participants.count() > k:
                user_2 = participants[k]
                user_2.index = index
                user_2.save()
            else:
                user_2 = None
            self.matches.create(n=index, stage=first_stage, user_1=user_1, user_2=user_2)
            self.nb_matches = index
        self.save()
        start_tournament_sse(self)
        time.sleep(3)
        for matche in self.matches.all():
            matche.post()
        return result


class TournamentStageSerializer(Serializer):
    class Meta:
        model = TournamentStage
        fields = [
            'id',
            'label',
            'stage',
        ]



class TournamentParticipantsSerializer(Serializer):
    id = serializers.IntegerField(source='user_id', read_only=True)
    tournament = serializers.CharField(max_length=4, source='tournament.code', read_only=True)

    class Meta:
        model = TournamentParticipants
        fields = [
            'id',
            'tournament',
            'stage',
            'seed',
            'still_in',
            'creator',
            'join_at',
        ]
        read_only_fields = [
            'id',
            'tournament',
            'stage',
            'seed',
            'still_in',
            'creator',
            'join_at',
        ]

    def create(self, validated_data):
        user = self.context['auth_user']
        tournament = get_tournament(create=True, code=self.context.get('code'))

        try:
            user = tournament.participants.get(user_id=user['id'], connected=False)
            user.reconnect()
            return user
        except TournamentParticipants.DoesNotExist:
            pass

        verify_place(user, tournament)

        if tournament.created_by == user['id']:
            validated_data['creator'] = True
        validated_data['user_id'] = user['id']
        validated_data['trophies'] = user['trophies']
        validated_data['tournament'] = tournament
        result = super().create(validated_data)
        create_player_instance(self.context['request'])
        return result

