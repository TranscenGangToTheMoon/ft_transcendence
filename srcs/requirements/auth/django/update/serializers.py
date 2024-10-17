from django.contrib.auth.models import User
from rest_framework import serializers

from auth.validators import validate_username


class UpdateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(validators=[validate_username], write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password']

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password is not None:
            instance.set_password(password)
        return super().update(instance, validated_data)
