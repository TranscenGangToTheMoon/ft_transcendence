from rest_framework import serializers
from lib_transcendence.serializer import Serializer

from stats.utils import get_trophies
from users.models import Users


class LargeUsersSerializer(Serializer):
    status = serializers.SerializerMethodField(read_only=True)
    trophies = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Users
        fields = [
            'id',
            'username',
            'profile_picture',
            'trophies',
            'status',
        ]
        read_only_fields = [
            'id',
            'username',
            'profile_picture',
            'trophies',
            'status',
        ]

    @staticmethod
    def get_status(obj):
        return {
            'is_online': obj.is_online,
            'game_playing': obj.game_playing,
            'last_online': obj.last_online,
        }

    @staticmethod
    def get_trophies(obj):
        return get_trophies(obj)


class SmallUsersSerializer(Serializer):

    class Meta:
        model = Users
        fields = [
            'id',
            'username',
            'profile_picture',
        ]
        read_only_fields = [
            'id',
            'username',
            'profile_picture',
        ]
