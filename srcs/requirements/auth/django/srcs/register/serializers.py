from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

from auth.validators import validate_username


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

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )

        refresh_token = RefreshToken.for_user(user)
        return {'refresh': str(refresh_token), 'access': str(refresh_token.access_token),}
