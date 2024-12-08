import random
import string
from typing import Literal

from lib_transcendence.exceptions import MessagesException
from rest_framework.exceptions import APIException


def generate_code(model=None, k=4, filter_field: Literal['code', 'username'] = 'code'):
    for _ in range(100000):
        code = ''.join(random.choices(string.digits, k=k))
        if model is None:
            return code
        kwargs = {filter_field: code}
        if not model.objects.filter(**kwargs).exists():
            return code
    raise APIException(MessagesException.InternalServerError.CODE_GENERATION)


def generate_guest_username(users_model):
    return 'Guest' + generate_code(users_model, 6, 'username')
