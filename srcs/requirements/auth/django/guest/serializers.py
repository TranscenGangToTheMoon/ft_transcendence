from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from guest.group import get_group_guest


class GuestTokenSerializer(serializers.ModelSerializer):
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ['access', 'refresh']

    def create(self, validated_data):
        guest_username = 'Guest' + "".join(choices(digits, k=6))
        user = User.objects.create_user(username=guest_username)
        guest_group = get_group_guest()
        user.groups.add(guest_group)
        refresh_token = RefreshToken.for_user(user)
        return {'access': str(refresh_token.access_token), 'refresh': str(refresh_token)}
