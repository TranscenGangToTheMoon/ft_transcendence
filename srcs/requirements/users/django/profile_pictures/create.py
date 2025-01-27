from profile_pictures.data import ProfilePicture, profile_pictures


def create_user_profile_pictures(user):
    for profile_picture in profile_pictures:
        profile_picture_model = user.profile_pictures.create(**profile_picture.dump())
        if profile_picture.name == ProfilePicture.DEFAULT:
            profile_picture_model.unlock()
            profile_picture_model.use()
