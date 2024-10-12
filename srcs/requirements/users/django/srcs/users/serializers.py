from rest_framework import serializers

from users.models import Users


class UsersSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    is_guest = serializers.BooleanField(read_only=True)
    profile_picture = serializers.IntegerField(read_only=True)
    coins = serializers.IntegerField(read_only=True)
    trophy = serializers.IntegerField(read_only=True)
    current_rank = serializers.IntegerField(read_only=True)
    accept_friend_request = serializers.BooleanField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Users
        fields = [
            'id',
            'username',
            'password',
            'is_guest',
            'profile_picture',
            'coins',
            'trophy',
            'current_rank',
            'accept_friend_request',
        ]
