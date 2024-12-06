from django.contrib.auth.models import User
from rest_framework import serializers

from guest.group import is_guest


class VerifyUserSerializer(serializers.ModelSerializer):
    is_guest = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'is_guest']

    @staticmethod
    def get_is_guest(obj):
        return is_guest(user=obj)
