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


def publish_event(user_id, event: Event, data=None):
    channel = f'events:user_{user_id}'

    try:
        message = {
            'service': event.service,
            'event_code': event.name,
            'type': event['type'],
            'message': event['message'],
            'target': event['target'],
        }
        if data is not None:
            message['data'] = data
        redis_client.publish(channel, json.dumps(message))
    except redis.exceptions.ConnectionError:
        raise ServiceUnavailable('event-queue')
