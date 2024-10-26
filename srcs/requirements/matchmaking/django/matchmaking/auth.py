import random
import string

from rest_framework import permissions, serializers

from matchmaking.request import requests_users


class IsAuthenticated(permissions.BasePermission):

    def has_permission(self, request, view):
        json_data = requests_users(request, 'me/', 'GET')
        request.data['auth_user'] = json_data
        request.user.id = json_data['id']
        request.user.username = json_data['username']
        return True


def get_auth_user(request=None):
    if request is None:
        raise serializers.ValidationError({'detail': 'Request is required.'})
    return request.data['auth_user']


def generate_code():
    return ''.join(random.choices(string.digits, k=4))
