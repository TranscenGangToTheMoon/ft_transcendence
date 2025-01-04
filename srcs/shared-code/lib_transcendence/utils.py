from datetime import datetime


def get_host(request):
    return request.get_host().split(':')[0]


def datetime_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError
