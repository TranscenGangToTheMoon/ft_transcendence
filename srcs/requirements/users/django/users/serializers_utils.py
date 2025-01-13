from rest_framework import serializers

from stats.utils import get_trophies
from users.models import Users


class SmallUsersSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField(read_only=True)
    trophies = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Users
        fields = [
            'id',
            'username',
            'is_guest',
            'profile_picture',
            'trophies',
            'status',
        ]
        read_only_fields = [
            'id',
            'username',
            'is_guest',
            'profile_picture',
            'trophies',
            'status',
        ]

    @staticmethod
    def get_status(obj):
        if obj.is_online:
            return 'online'
        else:
            return obj.last_online

    @staticmethod
    def get_trophies(obj):
        return get_trophies(obj)
