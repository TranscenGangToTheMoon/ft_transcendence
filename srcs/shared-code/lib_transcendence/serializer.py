from rest_framework import generics


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
