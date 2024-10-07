from rest_framework import serializers

from users.models import Users


def validate_username(value):
    if value == "me":
        raise serializers.ValidationError("Username can't be 'me'")
    qs = Users.objects.filter(username__iexact=value) #iexact == case insensitive
    if qs.exists():
        raise serializers.ValidationError("Username already exists")
    if value is not None:
        value = value.upper()
    return value
