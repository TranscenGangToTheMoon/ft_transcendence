import json

import redis
from lib_transcendence.exceptions import ServiceUnavailable
from lib_transcendence.sse_event import Event


# todo reset to 0 notfication when sended
# todo handle notification for chat
# todo when retrieve many user, handle friend field
# todo when create match return user instance not only id
# todo when create match return teams id not list


redis_client = redis.StrictRedis(host='event-queue')


def publish_event(user_id, event_code: EventCode, data=None):
    channel = f'events:user_{user_id}'
    event = globals().get(event_code.value.replace('-', '_'))
    if event is None:
        raise ParseError({'event_code': [MessagesException.ValidationError.INVALID_EVENT_CODE]}) # todo handle error

    print('EVENT', event, type(event), flush=True)
    try:
        redis_client.publish(channel, json.dumps(event.get_dict(data)))
    except redis.exceptions.ConnectionError:
        raise ServiceUnavailable('event-queue')
