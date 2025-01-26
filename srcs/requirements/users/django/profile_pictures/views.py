from rest_framework import generics
from rest_framework.exceptions import NotFound

from lib_transcendence.exceptions import MessagesException
from profile_pictures.models import ProfilePictures
from profile_pictures.serializers import ProfilePicturesSerializer
from users.auth import get_user


class ProfilePicturesView(generics.ListAPIView):
    serializer_class = ProfilePicturesSerializer
    pagination_class = None

    def get_queryset(self):
        return get_user(self.request).profile_pictures.all().order_by('is_equiped', 'is_unlocked', 'n')


class SetProfilePictureView(generics.UpdateAPIView):
    serializer_class = ProfilePicturesSerializer

    def get_object(self):
        try:
            return get_user(self.request).profile_pictures.get(n=self.kwargs['id'])
        except ProfilePictures.DoesNotExist:
            raise NotFound(MessagesException.NotFound.PROFILE_PICTURE)


profile_pictures_view = ProfilePicturesView.as_view()
set_profile_picture_view = SetProfilePictureView.as_view()
