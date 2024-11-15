from rest_framework import generics

from blocking.models import BlockedUsers
from blocking.serializers import BlockedSerializer


class BlockedMixin(generics.GenericAPIView):
    queryset = BlockedUsers.objects.all()
    serializer_class = BlockedSerializer


class BlockedListCreateView(generics.ListCreateAPIView, BlockedMixin):
    pass


class BlockedDeleteView(generics.DestroyAPIView, BlockedMixin):
    def get_object(self):
        try:
            return self.get_queryset().get(id=self.kwargs['pk'], user_id=self.request.user.id)
        except BlockedUsers.DoesNotExist:
            raise PermissionDenied(MessagesException.PermissionDenied.NOT_BELONG_BLOCKED)


blocked_list_create_view = BlockedListCreateView.as_view()
blocked_delete_view = BlockedDeleteView.as_view()
