import requests
from rest_framework import permissions
from rest_framework.exceptions import AuthenticationFailed


class IsAuthenticated(permissions.BasePermission):

    def has_permission(self, request, view):
        token = request.headers.get('Authorization')

        if not token:
            raise AuthenticationFailed('Authentication credentials were not provided.')

        try:
            response = requests.get(
                'http://auth:8000/api/auth/verify/',
                headers={
                    'Authorization': token,
                    'Content-Type': 'application/json'
                }
            )
            assert response.status_code == 200
        except (requests.ConnectionError, AssertionError, requests.exceptions.JSONDecodeError) as e:
            raise AuthenticationFailed(f'Failed to connect to auth service {e}')

        return True
