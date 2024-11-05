import random
import string

from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied


def generate_code(model):
    for _ in range(100000):
        code = ''.join(random.choices(string.digits, k=4))
        if not model.objects.filter(code=code).exists():
            return code
    raise PermissionDenied('Code generation failed.')


def validate_type(value, name, choices):
    if value not in choices:
        error_message = ''
        for choice in choices:
            error_message += f"'{choice}'"
            if choice == choices[-2]:
                error_message += ' or '
            elif choice != choices[-1]:
                error_message += ', '
        raise serializers.ValidationError([f'{name} must be {error_message}.'])
    return value
