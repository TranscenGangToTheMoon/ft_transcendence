from profile_pictures.data import ProfilePictures, profile_pictures


def create_user_profile_pictures(user):
    for profile_picture in profile_pictures:
        profile_picture_model = user.profile_pictures.create(**profile_picture)
        if profile_picture.name == ProfilePictures.DEFAULT:
            profile_picture_model.unlock()
