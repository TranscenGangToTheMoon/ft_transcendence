from rest_framework import serializers

from lib_transcendence.serializer import Serializer
from profile_pictures.models import ProfilePictures


class ProfilePicturesSerializer(Serializer):
    unlock = serializers.BooleanField(source='is_unlocked')

    class Meta:
        model = ProfilePictures
        fields = [
            'id',
            'name',
            'unlock_reason',
            'unlock',
            'url',
            'small',
            'medium',
            'large',
        ]
        read_only_fields = [
            'id',
            'name',
            'unlock',
            'url',
            'small',
            'medium',
            'large',
        ]
