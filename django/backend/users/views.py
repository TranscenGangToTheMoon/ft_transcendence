import random
import string

from django.forms import model_to_dict
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response

from users.models import Users
from users.serializer import UsersSerializer


# Create your views here.
class UsersMixinView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    lookup_field = 'pk'











@api_view(["GET"])
def user_index(request):
    instance = Users.objects.all()
    data = {}
    print(instance)
    if instance:
        for user in instance:
            print(user)
            # data[users.id] = UsersSerializer(users).data
            data[user.id] = model_to_dict(user)
    return Response(data)
    # data = {}
    # instance = Users.objects.all().order_by("?").first()
    # data = {}
    # if instance:
    #     data = UsersSerializer(instance).data
    # return Response(data)


@api_view(["POST"])
def user_index_post(request):
    serializer = UsersSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        data = serializer.data
        serializer.save()
        print(data)
        return Response(data)
    return Response({"error": "invalid data type"})


class UsersDetailView(generics.RetrieveAPIView):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    # lookup_field = "username"


class UsersUpdateView(generics.UpdateAPIView):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    lookup_field = "pk"

    def perform_update(self, serializer):
        instance = serializer.save()


class UsersDeleteView(generics.DestroyAPIView):
    #  return 204 if delete object
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    lookup_field = "pk"

    def perform_destroy(self, instance):
        super().perform_destroy(instance)


class UsersListDetailView(generics.ListAPIView):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    # lookup_field = "username"


class UsersCreateView(generics.CreateAPIView):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer

    def perform_create(self, serializer):
        print(serializer.validated_data.get('username'))
        kwarg = {}
        if serializer.validated_data.get('username') is None:
            kwarg['username'] = 'Guest' + ''.join(random.choices(string.digits, k=5))
        serializer.save(**kwarg)


def user_alt_view(request):
    method = request.method
    if method == "GET":
        pass
    if method == "POST":
        pass

