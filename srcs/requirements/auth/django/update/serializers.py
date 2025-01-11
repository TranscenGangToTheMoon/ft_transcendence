from django.contrib.auth.models import User
from lib_transcendence import endpoints
from lib_transcendence.services import request_chat
from rest_framework import serializers
from rest_framework.exceptions import APIException

from auth.validators import validate_username, set_password
from guest.group import is_guest


class UpdateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True, validators=[validate_username])
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password']

    def update(self, instance, validated_data):
        old_username = instance.username
        password = validated_data.pop('password', None)
        result = super().update(instance, validated_data)
        set_password(password, result, check_previous_password=True, old_username=old_username)
        if 'username' in validated_data and not is_guest(user=instance):
            try:
                request_chat(endpoints.UsersManagement.frename_user.format(user_id=instance.id), method='PUT', data={'username': validated_data['username']})
            except APIException:
                pass
        return result
