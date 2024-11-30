from rest_framework import generics
from rest_framework.exceptions import NotAuthenticated, NotFound
from lib_transcendence.exceptions import MessagesException

from users.auth import auth_delete, get_valid_user, get_user
from users.models import Users
from users.serializers import UsersSerializer, UsersMeSerializer


class UsersMeView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UsersMeSerializer

    def get_object(self):
        try:
            return Users.objects.get(id=self.request.user.id)
        except Users.DoesNotExist:
            raise NotFound(MessagesException.NotFound.USER)

    def destroy(self, request, *args, **kwargs):
        password = self.request.data.get('password')
        if password is None:
            raise NotAuthenticated({'password': 'Password confirmation is required to delete the account.'})
        auth_delete(self.request.headers.get('Authorization'), {'password': password})
        return super().destroy(request, *args, **kwargs)


class UserRetrieveView(generics.RetrieveAPIView):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer

    def get_object(self):
        return get_valid_user(get_user(self.request), False, id=self.kwargs['user_id'])


users_me_view = UsersMeView.as_view()
user_retrieve_view = UserRetrieveView.as_view()
