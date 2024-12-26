from lib_transcendence.services import create_sse_event
from lib_transcendence.users import retrieve_users
from lib_transcendence.sse_events import EventCode


def send_sse_event(event: EventCode, instance, data=None, request=None, exclude_myself=True):
    if data is None:
        data = {}
    members = instance.place.participants
    if exclude_myself:
        members = members.exclude(id=instance.id)
    other_members = list(members.values_list('user_id', flat=True))
    if other_members:
        if request is not None:
            user_instance = retrieve_users(instance.user_id, request)
            data.update(user_instance[0])
        create_sse_event(other_members, event, data=data)
