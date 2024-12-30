from rest_framework import serializers

from users.models import Users


class SmallUsersSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField(read_only=True)
    status = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Users
        fields = [
            'id',
            'username',
            'is_guest',
            'profile_picture',
            'current_rank',
            'status',
        ]
        read_only_fields = [
            'id',
            'username',
            'is_guest',
            'profile_picture',
            'current_rank',
            'status',
        ]

    @staticmethod
    def get_status(obj):
        if obj.is_online:
            return 'online'
        else:
            return obj.last_online
