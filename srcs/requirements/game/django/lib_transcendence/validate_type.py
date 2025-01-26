from rest_framework import serializers


def validate_type(value, obj, choices=None):
    if choices is None:
        choices = obj.attr()
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
        raise serializers.ValidationError([f'{obj()} must be {error_message}.'])
    return value


def surchage_list(obj):
    choices = []
    for attr in dir(obj):
        if attr.startswith('__'):
            return choices
        choices.append(getattr(obj, attr))
