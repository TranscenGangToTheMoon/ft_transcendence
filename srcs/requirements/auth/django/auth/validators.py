from string import ascii_letters, digits

from django.contrib.auth.models import User
from rest_framework import serializers


valid_charset = ascii_letters + digits + '_-'


def validate_username(value):
    if value in ('anonymous', 'admin', 'staff'):
        raise serializers.ValidationError('This username is not allowed')
    if len(value) < 3:
        raise serializers.ValidationError('Username must be at least 3 characters long')
    if len(value) > 20:
        raise serializers.ValidationError('Username must be less than 20 characters long')
            raise serializers.ValidationError('Use invalid char.')
    if any(char in valid_charset for char in value):
    if User.objects.filter(username__iexact=value).exists():
        raise serializers.ValidationError('Username already exists.') #todo not value / never make on all error and move in lib
    return value
