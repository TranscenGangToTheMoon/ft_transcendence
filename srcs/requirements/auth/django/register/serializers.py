from django.contrib.auth.models import User
from lib_transcendence.exceptions import MessagesException
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from auth.validators import validate_username
from guest.group import get_group_guest


class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            'username',
            'password',
            'access',
            'refresh',
        ]

    def validated_username(self, value):
        request = self.context.get('request')

        if request is None:
            raise serializers.ValidationError(MessagesException.ValidationError.REQUEST_REQUIRED)

        return validate_username(value, request.method == 'POST')

    def create(self, validated_data):
        instance = super().create(validated_data)
        refresh_token = RefreshToken.for_user(instance)
        return {'access': str(refresh_token.access_token), 'refresh': str(refresh_token)}

    def update(self, instance, validated_data):
        guest_group = get_group_guest()
        instance.groups.remove(guest_group)
        password = validated_data.pop('password', None)
        if password is not None:
            instance.set_password(password)
        super().update(instance, validated_data)

        refresh_token = RefreshToken.for_user(instance)
        return {'access': str(refresh_token.access_token), 'refresh': str(refresh_token)}

