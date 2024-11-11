from rest_framework import generics


class SerializerContext(generics.GenericAPIView): # todo use in all
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['code'] = self.kwargs.get('code')
        context['auth_user'] = self.request.data['auth_user']
        return context
