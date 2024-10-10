from random import choices
from string import digits

from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from auth.validators import validate_username
from guest.group import get_group_guest


class GuestTokenSerializer(serializers.ModelSerializer):
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ['access', 'refresh']

    def create(self, validated_data):
        guest_username = 'Guest' + "".join(choices(digits, k=4))
        user = User.objects.create_user(username=guest_username)
        guest_group = get_group_guest()
        user.groups.add(guest_group)
        refresh_token = RefreshToken.for_user(user)
        return {'refresh': str(refresh_token), 'access': str(refresh_token.access_token),}


class GuestRegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(validators=[validate_username])

    class Meta:
        model = User
        fields = ['username', 'password']

    def update(self, instance, validated_data):
        guest_group = get_group_guest()
        instance.groups.remove(guest_group)
        return super().update(instance, validated_data)
