from django.contrib.auth.models import Group

group_guests = 'Guests'


def get_group_guest():
    try:
        guest_group = Group.objects.get(name=group_guests)
    except Group.DoesNotExist:
        guest_group = Group.objects.create(name=group_guests)
    return guest_group


def is_guest(request=None, user=None):
    if user is None:
        user = request.user
    return user.groups.filter(name=group_guests).exists()
