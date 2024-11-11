from django.contrib.auth.models import User
from rest_framework import serializers

from guest.group import group_guests


class VerifyUserSerializer(serializers.ModelSerializer):
    is_guest = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'is_guest']

    @staticmethod
    def get_is_guest(obj):
        return obj.groups.filter(name=group_guests).exists()
