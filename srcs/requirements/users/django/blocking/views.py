from lib_transcendence.exceptions import MessagesException
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied

from blocking.models import BlockedUsers
from blocking.serializers import BlockedSerializer


class BlockedMixin(generics.GenericAPIView):
    queryset = BlockedUsers.objects.all()
    serializer_class = BlockedSerializer


class BlockedView(generics.ListCreateAPIView, BlockedMixin):
    def filter_queryset(self, queryset):
        return queryset.filter(user_id=self.request.user.id)


class DeleteBlockedView(generics.DestroyAPIView, BlockedMixin):
    def get_object(self):
        try:
            return self.get_queryset().get(id=self.kwargs['blocking_id'], user_id=self.request.user.id)
        except BlockedUsers.DoesNotExist:
            raise PermissionDenied(MessagesException.PermissionDenied.NOT_BELONG_BLOCKED)

    def perform_destroy(self, instance):
        instance.blocked_services('unblock')
        return super().perform_destroy(instance)


blocked_view = BlockedView.as_view()
delete_blocked_view = DeleteBlockedView.as_view()
