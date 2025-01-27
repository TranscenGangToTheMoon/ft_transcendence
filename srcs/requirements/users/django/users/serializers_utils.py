from rest_framework import serializers
from lib_transcendence.serializer import Serializer
from profile_pictures.serializers import SmallProfilePicturesSerializer

from stats.utils import get_trophies
from users.models import Users


class BaseUsersSerializer(Serializer):
    profile_picture = serializers.SerializerMethodField(read_only=True)

    @staticmethod
    def get_profile_picture(obj):
        return SmallProfilePicturesSerializer(obj.profile_pictures.get(is_equiped=True)).data

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


class LargeUsersSerializer(BaseUsersSerializer):
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


class SmallUsersSerializer(BaseUsersSerializer):

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
