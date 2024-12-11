from django.contrib.auth.models import User
from lib_transcendence.exceptions import MessagesException
from rest_framework import serializers

from auth.utils import create_user_get_token
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

    def validate_username(self, value):
        request = self.context.get('request')
        if request is None:
            raise serializers.ValidationError(MessagesException.ValidationError.REQUEST_REQUIRED)

        return validate_username(value, request.method == 'POST')

    def create(self, validated_data):
        password = validated_data.pop('password')
        instance = super().create(validated_data)
        instance.set_password(password)
        instance.save()
        return create_user_get_token(instance)

    def update(self, instance, validated_data):
        guest_group = get_group_guest()
        instance.groups.remove(guest_group)
        password = validated_data.pop('password', None)
        if password is not None:
            instance.set_password(password)
        if validated_data['username'] == instance.username:
            validated_data.pop('username')
        else:
            validate_username(validated_data['username'], only_check_exists=True)
        new_instance = super().update(instance, validated_data)
        return create_user_get_token(new_instance, False)
