from string import ascii_letters, digits

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers

from lib_transcendence.exceptions import MessagesException

valid_charset = ascii_letters + digits + '_-'
valid_password_charset = valid_charset + '!@#$%^&*()'


def validate_username(value, check_exists=True, only_check_exists=False):
    if not only_check_exists:
        not_allowed = ('anonymous', 'admin', 'staff', 'support', 'ft_transcendence', 'transcendence')
        for not_allowed_value in not_allowed:
            if not_allowed_value in value:
                raise serializers.ValidationError(MessagesException.ValidationError.USERNAME_NOT_ALLOWED)
        if len(value) < 3:
            raise serializers.ValidationError(MessagesException.ValidationError.USERNAME_LONGER_THAN_3_CHAR)
        if any(char not in valid_charset for char in value):
            raise serializers.ValidationError(MessagesException.ValidationError.INVALIDE_CHAR)
    if (check_exists or only_check_exists) and User.objects.filter(username__iexact=value).exists():
        exception_msg = MessagesException.ValidationError.USERNAME_ALREAY_EXISTS
        if only_check_exists:
            exception_msg = {'username': [exception_msg]}
        raise serializers.ValidationError(exception_msg)
    return value


def set_password(password, user, remove_instance=False, check_previous_password=False, old_username=None):
    if password is None:
        return
    try:
        if check_previous_password and user.check_password(password):
            raise ValidationError(MessagesException.ValidationError.SAME_PASSWORD)
        if len(password) > 50:
            raise ValidationError(MessagesException.ValidationError.PASSWORD_SHORTER_THAN_50_CHAR)
        if any(char not in valid_password_charset for char in password):
            raise ValidationError(MessagesException.ValidationError.INVALIDE_CHAR)
        validate_password(password, user)
    except ValidationError as e:
        if remove_instance:
            user.delete()
        if old_username:
            user.username = old_username
            user.save()
        raise serializers.ValidationError({'password': e.messages})
    user.set_password(password)
    user.save()
