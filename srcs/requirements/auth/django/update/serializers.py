from django.contrib.auth.models import User
from lib_transcendence import endpoints
from lib_transcendence.exceptions import MessagesException
from lib_transcendence.services import request_chat
from rest_framework import serializers
from rest_framework.exceptions import APIException
from lib_transcendence.serializer import Serializer

from auth.validators import validate_username, set_password
from guest.group import is_guest


class UpdateSerializer(Serializer):
    username = serializers.CharField(write_only=True, validators=[validate_username])
    password = serializers.CharField(write_only=True)
    old_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            'username',
            'password',
            'old_password',
        ]

    def update(self, instance, validated_data):
        old_username = instance.username
        password = validated_data.pop('password', None)
        if password is not None:
            old_password = validated_data.pop('old_password', None)
            if old_password is None:
                raise serializers.ValidationError({'old_password': [MessagesException.Authentication.PASSWORD_CONFIRMATION_REQUIRED]})
            if not instance.check_password(old_password):
                raise serializers.ValidationError({'old_password': [MessagesException.Authentication.INCORRECT_PASSWORD]})
        result = super().update(instance, validated_data)
        set_password(password, result, check_previous_password=True, old_username=old_username)
        if 'username' in validated_data and not is_guest(user=instance):
            try:
                request_chat(endpoints.UsersManagement.frename_user.format(user_id=instance.id), method='PUT', data={'username': validated_data['username']})
            except APIException:
                pass
        return result
