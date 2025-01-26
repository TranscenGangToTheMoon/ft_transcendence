from rest_framework.exceptions import APIException, PermissionDenied
from rest_framework.pagination import LimitOffsetPagination as LimitOffsetPaginationRestFramework

from lib_transcendence.exceptions import ServiceUnavailable


class LimitOffsetPagination(LimitOffsetPaginationRestFramework):

    def get_next_link(self):
        next_link = super().get_next_link()
        if next_link is not None:
            return '/' + next_link.split(self.request.build_absolute_uri('/'))[-1]
        return None

    def get_previous_link(self):
        previous_link = super().get_previous_link()
        if previous_link is not None:
            return '/' + previous_link.split(self.request.build_absolute_uri('/'))[-1]
        return None


def get_all_pagination_items(request_service, service, endpoint, **kwargs):
    result = []
    while True:
        try:
            response = request_service(endpoint, 'GET', **kwargs)
            result += response['results']
            if response['next'] is None:
                break
            endpoint = response['next']
        except PermissionDenied:
            return result
        except APIException:
            raise ServiceUnavailable(service)
    return result
