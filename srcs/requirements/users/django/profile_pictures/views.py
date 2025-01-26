from rest_framework import generics

from profile_pictures.serializers import ProfilePicturesSerializer
from users.auth import get_user


class ProfilePicturesView(generics.ListAPIView):
    serializer_class = ProfilePicturesSerializer
    pagination_class = None

    def get_queryset(self):
        return get_user(self.request).profile_pictures.all().order_by('is_unlocked')


profile_pictures_view = ProfilePicturesView.as_view()
