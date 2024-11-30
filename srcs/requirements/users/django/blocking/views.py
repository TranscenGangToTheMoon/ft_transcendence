from lib_transcendence.exceptions import MessagesException
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied

from blocking.models import BlockedUsers
from blocking.serializers import BlockedSerializer


class BlockedMixin(generics.GenericAPIView):
    queryset = BlockedUsers.objects.all()
    serializer_class = BlockedSerializer


class BlockedListCreateView(generics.ListCreateAPIView, BlockedMixin):
    def filter_queryset(self, queryset):
        return queryset.filter(user_id=self.request.user.id)


class BlockedDeleteView(generics.DestroyAPIView, BlockedMixin):
    def get_object(self):
        try:
            return self.get_queryset().get(id=self.kwargs['blocking_id'], user_id=self.request.user.id)
        except BlockedUsers.DoesNotExist:
            raise PermissionDenied(MessagesException.PermissionDenied.NOT_BELONG_BLOCKED)

    def perform_destroy(self, instance):
        instance.blocked_services('unblock')
        return super().perform_destroy(instance)


blocked_list_create_view = BlockedListCreateView.as_view()
blocked_delete_view = BlockedDeleteView.as_view()
