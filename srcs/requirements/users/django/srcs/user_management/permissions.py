from rest_framework import permissions, serializers

from user_management.auth import auth_verify
from users.models import Users


class IsAuthenticated(permissions.BasePermission):

    def has_permission(self, request, view):
        auth_verify(request.headers.get('Authorization'))
        return True


def get_object(request):
    if request is None:
        raise serializers.ValidationError({'error': 'Request must be provided.'})

    json_data = auth_verify(request.headers.get('Authorization'))

    try:
        user = Users.objects.get(id=json_data['id'])
        if user.is_guest != json_data['is_guest']:
            user.update(is_guest=json_data['is_guest'])
        return user
    except Users.DoesNotExist:
        return Users.objects.create(**json_data)
