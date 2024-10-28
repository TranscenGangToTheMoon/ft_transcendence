from typing import Literal

from rest_framework import serializers


def get_participants(name: Literal['lobby', 'tournament'], model, obj, user_id, creator_check):
    kwargs = {'user_id': user_id}
    if obj is not None:
        kwargs[name] = obj.id

    try:
        p = model.objects.get(**kwargs)
        if creator_check and not p.creator:
            raise serializers.ValidationError({'detail': f'You are not creator of this {name}.'})
        return p
    except model.DoesNotExist:
        if obj is None:
            raise serializers.ValidationError({'detail': f'You are not in any {name}.'})
        raise serializers.ValidationError({'detail': f'You are not participant of this {name}.'})
