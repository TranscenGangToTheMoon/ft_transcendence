from django.contrib.auth.models import Group

group_guests = 'Guests'


def get_group_guest():
    return Group.objects.get_or_create(name=group_guests)[0]


def is_guest(request=None, user=None):
    if user is None:
        user = request.user
    return user.groups.filter(name=group_guests).exists()
