from rest_framework import generics
from rest_framework import serializers
from lib_transcendence.exceptions import Throttled
from django.db import IntegrityError


class SerializerKwargsContext(generics.GenericAPIView):

    def get_serializer_context(self):
        context = super().get_serializer_context()
        for k, v in self.kwargs.items():
            context[k] = v
        return context


class SerializerAuthContext(SerializerKwargsContext):

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['auth_user'] = self.request.data['auth_user']
        return context


class Serializer(serializers.ModelSerializer):
    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError:
            raise Throttled()

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except IntegrityError:
            raise Throttled()
