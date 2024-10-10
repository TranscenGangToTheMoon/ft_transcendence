from random import choices
from string import digits

from django.contrib.auth.models import User, Group
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from auth.static import group_guests
from auth.validators import validate_username

try:
    guest_group = Group.objects.get(name=group_guests)
except Group.DoesNotExist:
    guest_group = None


class GuestTokenSerializer(serializers.ModelSerializer):
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ['access', 'refresh']

    def create(self, validated_data):
        guest_username = 'Guest' + "".join(choices(digits, k=4))
        user = User.objects.create_user(username=guest_username)
        if guest_group is None:
            raise serializers.ValidationError({'group': f'group \'{group_guests}\' not found'})
        user.groups.add(guest_group)
        refresh_token = RefreshToken.for_user(user)
        return {'refresh': str(refresh_token), 'access': str(refresh_token.access_token),}


class GuestRegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(validators=[validate_username])

    class Meta:
        model = User
        fields = ['username', 'password']

    def update(self, instance, validated_data):
        if guest_group is None:
            raise serializers.ValidationError({'group': f'group \'{group_guests}\' not found'})
        instance.groups.remove(guest_group)
        return super().update(instance, validated_data)
