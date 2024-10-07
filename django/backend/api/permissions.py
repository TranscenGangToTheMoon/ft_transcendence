from rest_framework import permissions


# Custom permissions
class IsStaffEditorPermission(permissions.DjangoModelPermissions):
    # def has_permission(self, request, view):
    #     # if request.method in permissions.SAFE_METHODS:
    #     #     return True
    #     print(request.user.get_all_permissions())
    #     if request.user.is_staff or request.user.has_perm('users.view_users'): # add delete change view
    #         return True
    #     return False

    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }

    # def has_permission(self, request, view):
    #     print(request.user.get_all_permissions())
    #     if not request.user.is_staff:
    #         return False
    #     return super().has_permission(request, view)

    # def has_object_permission(self, request, view, obj):
    #     print(obj)
    #     print("hey salut comment ca")
    #     return obj.pk == request.user.pk


class IsMePermission(permissions.DjangoModelPermissions):
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': [],
        'HEAD': [],
        'POST': [],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }

    def has_object_permission(self, request, view, obj):
        return obj.pk == request.user.pk
