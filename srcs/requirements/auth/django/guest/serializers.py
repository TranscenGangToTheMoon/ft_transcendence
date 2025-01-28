from django.contrib.auth.models import User
from rest_framework import serializers

from auth.utils import create_user_get_token
from guest.group import get_group_guest
from lib_transcendence.generate import generate_guest_username
from lib_transcendence.serializer import Serializer


class GuestTokenSerializer(Serializer):
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ['access', 'refresh']

    def create(self, validated_data):
        guest_username = generate_guest_username(User)
        user = User.objects.create_user(username=guest_username)
        guest_group = get_group_guest()
        user.groups.add(guest_group)
        return create_user_get_token(user)
