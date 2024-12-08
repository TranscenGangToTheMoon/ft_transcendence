
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
