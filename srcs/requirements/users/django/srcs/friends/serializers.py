from rest_framework import serializers

from friends.models import Friends, FriendRequests
from user_management.auth import auth_verify
from user_management.permissions import get_object
from users.models import Users


class FriendsManagementSerializer(serializers.Serializer):
    pass
    # username = serializers.CharField()

    # def validate(self, data):
    #     try:
    #         friend = Users.objects.get(username=data['username'])
    #     except Users.DoesNotExist:
    #         raise serializers.ValidationError("This user does not exist.")
    #
    #     data['friend'] = friend
    #     return data

