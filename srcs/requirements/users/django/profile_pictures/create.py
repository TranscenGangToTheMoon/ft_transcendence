from profile_pictures.data import ProfilePicture, profile_pictures


def create_user_profile_pictures(user):
    for profile_picture in profile_pictures:
        profile_picture_model = user.profile_pictures.create(**profile_picture.dump())
        if profile_picture.name == ProfilePicture.REGISTER and not user.is_guest:
            profile_picture_model.unlock()
            profile_picture_model.use()
        elif profile_picture.name == ProfilePicture.GUEST and user.is_guest:
            profile_picture_model.unlock()
            profile_picture_model.use()
