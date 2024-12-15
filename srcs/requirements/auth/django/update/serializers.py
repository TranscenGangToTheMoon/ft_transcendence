from django.contrib.auth.models import User
from lib_transcendence import endpoints
from lib_transcendence.exceptions import MessagesException
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
        set_password(validated_data.pop('password', None), instance, check_previous_password=True)
        if 'username' in validated_data and not is_guest(user=instance):
            try:
                request_chat(endpoints.UsersManagement.frename_user.format(user_id=instance.id), data={'username': validated_data['username']})
            except APIException:
                pass
        return super().update(instance, validated_data)
