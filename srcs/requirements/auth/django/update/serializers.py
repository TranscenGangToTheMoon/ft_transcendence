from django.contrib.auth.models import User
from rest_framework import serializers
from lib_transcendence.exceptions import MessagesException

from auth.validators import validate_username


class UpdateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(validators=[validate_username], write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password']

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if instance.check_password(password):
            raise serializers.ValidationError({'password': [MessagesException.ValidationError.SAME_PASSWORD]})
        if password is not None:
            instance.set_password(password)
        return super().update(instance, validated_data)
