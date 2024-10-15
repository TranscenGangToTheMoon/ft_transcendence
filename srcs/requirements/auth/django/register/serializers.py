from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from auth.validators import validate_username
from guest.group import get_group_guest


class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(validators=[validate_username], write_only=True)
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

    def update(self, instance, validated_data):
        guest_group = get_group_guest()
        instance.groups.remove(guest_group)
        password = validated_data.pop('password', None)
        if password is not None:
            instance.set_password(password)
        super().update(instance, validated_data)

        refresh_token = RefreshToken.for_user(instance)
        return {'access': str(refresh_token.access_token), 'refresh': str(refresh_token)}

