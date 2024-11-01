from rest_framework import serializers

from tournaments.models import Tournaments, TournamentStage


class TournamentSerializer(serializers.ModelSerializer):
    stages = serializers.ListField(child=serializers.DictField(), write_only=True)

    class Meta:
        model = Tournaments
        fields = '__all__'

    def create(self, validated_data):
        stages = validated_data.pop('stages')
        result = super().create(validated_data)
        for stage in stages:
            stage['tournament'] = result
            TournamentStage.objects.create(**stage)
        return result
