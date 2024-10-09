import random
import string

from django.db.models.expressions import result
from rest_framework import generics, permissions

from api.permissions import IsMePermission
from users.models import Users
from users.serializers import UsersRetrieveSerializer, UsersMeSerializer


# Create your views here.
class UsersListCreateView(generics.ListCreateAPIView):
    queryset = Users.objects.all()
    serializer_class = UsersRetrieveSerializer

    # permission_classes = [permissions.IsAuthenticated]


    # def get_queryset(self, *args, **kwargs):
    #     request = self.request
    #     print(request)
    #     print(request.user)
    #     if not request.user.is_authenticated:
    #         return Users.objects.none()
    #     return super().get_queryset(*args, **kwargs)


users_list_create_view = UsersListCreateView.as_view()


class UsersRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Users.objects.all()
    serializer_class = UsersMeSerializer

    permission_classes = [IsMePermission]

    def get_object(self):
        me = self.queryset.get(id=self.request.user.id)
        if me is not None:
            return me
        return None


users_retrieve_update_delete_view = UsersRetrieveUpdateDeleteView.as_view()


class UsersRetrieveView(generics.RetrieveAPIView):
    queryset = Users.objects.all()
    serializer_class = UsersRetrieveSerializer
    lookup_field = 'pk'

    permission_classes = [permissions.IsAuthenticated]


users_retrieve_view = UsersRetrieveView.as_view()


class UsersSearchListView(generics.ListAPIView):
    queryset = Users.objects.all()
    serializer_class = UsersRetrieveSerializer

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        q = self.request.GET.get('q')
        results = Users.objects.none()
        if q is not None:
            user = None
            if self.request.user.is_authenticated:
                user = self.request.user
            results = qs.search(q, user)
        return results

# class UsersListCreateView(generics.ListCreateAPIView):
#     def perform_create(self, serializer):
#         kwarg = {}
#         if serializer.validated_data.get('username') is None:
#             kwarg['username'] = 'Guest' + ''.join(random.choices(string.digits, k=5))
#         serializer.save(**kwarg)


# users_mixin_view = UsersMixinView.as_view()
# users_list_create_view = UsersListCreateView.as_view()
