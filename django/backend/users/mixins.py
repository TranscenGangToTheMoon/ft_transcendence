from rest_framework import permissions

from api.permissions import IsStaffEditorPermission
from users.models import Users
from users.serializers import UsersRetrieveSerializer


class UsersMixin:
    queryset = Users.objects.all()
    serializer_class = UsersRetrieveSerializer
    lookup_field = 'pk'

    permission_classes = [
        permissions.IsAdminUser,
        IsStaffEditorPermission
    ]
