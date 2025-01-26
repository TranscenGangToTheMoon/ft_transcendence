from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from lib_transcendence.exceptions import MessagesException
from lib_transcendence.serializer import Serializer
from profile_pictures.models import ProfilePictures


class ProfilePicturesSerializer(Serializer):
    id = serializers.IntegerField(source='n', read_only=True)
    unlock = serializers.BooleanField(source='is_unlocked', read_only=True)

    class Meta:
        model = ProfilePictures
        fields = [
            'id',
            'name',
            'unlock_reason',
            'unlock',
            'is_equiped',
            'url',
            'small',
            'medium',
            'large',
        ]
        read_only_fields = [
            'id',
            'name',
            'unlock',
            'is_equiped',
            'url',
            'small',
            'medium',
            'large',
        ]

    def update(self, instance, validated_data):
        if instance.is_unlocked:
            raise PermissionDenied(MessagesException.PermissionDenied.PROFILE_PICTURE_LOCKED)
        instance.user.set_profile_picture(instance)
        return instance


class SmallProfilePicturesSerializer(Serializer):
    id = serializers.IntegerField(source='n', read_only=True)

    class Meta:
        model = ProfilePictures
        fields = [
            'id',
            'name',
            'small',
            'medium',
        ]
        read_only_fields = [
            'id',
            'name',
            'small',
            'medium',
        ]
