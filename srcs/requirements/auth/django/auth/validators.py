from string import ascii_letters, digits

from rest_framework import serializers
from lib_transcendence.exceptions import MessagesException
from django.contrib.auth.models import User


valid_charset = ascii_letters + digits + '_-'


def validate_username(value, check_exists=True, only_check_exists=False):
    if not only_check_exists:
        not_allowed = ('anonymous', 'admin', 'staff', 'support', 'ft_transcendence', 'transcendence')
        for not_allowed_value in not_allowed:
            if not_allowed_value in value:
                raise serializers.ValidationError(MessagesException.ValidationError.USERNAME_NOT_ALLOWED)
        if len(value) < 3:
            raise serializers.ValidationError(MessagesException.ValidationError.USERNAME_LONGER_THAN_3_CHAR)
        if len(value) > 30:
            raise serializers.ValidationError(MessagesException.ValidationError.USERNAME_SHORTER_THAN_30_CHAR)
        if any(char not in valid_charset for char in value):
            raise serializers.ValidationError(MessagesException.ValidationError.INVALIDE_CHAR)
    if (check_exists or only_check_exists) and User.objects.filter(username__iexact=value).exists():
        raise serializers.ValidationError(MessagesException.ValidationError.USERNAME_ALREAY_EXISTS)
    return value
