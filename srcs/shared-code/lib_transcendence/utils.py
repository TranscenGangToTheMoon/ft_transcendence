import random
import string

from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied


def generate_code(model=None, k=4):
    for _ in range(100000):
        code = ''.join(random.choices(string.digits, k=k))
        if model is None:
            return code
        if not model.objects.filter(code=code).exists():
            return code
    raise PermissionDenied('Code generation failed.')


#todo secure guest unique
def generate_guest_username():
    return 'Guest' + generate_code(k=6)


def validate_type(value, name, choices):
    if value not in choices:
        error_message = ''
        for choice in choices:
            if isinstance(choice, int):
                error_message += f"{choice}"
            else:
                error_message += f"'{choice}'"
            if choice == choices[-2]:
                error_message += ' or '
            elif choice != choices[-1]:
                error_message += ', '
        raise serializers.ValidationError([f'{name} must be {error_message}.'])
    return value


def get_host(request):
    return request.get_host().split(':')[0]
