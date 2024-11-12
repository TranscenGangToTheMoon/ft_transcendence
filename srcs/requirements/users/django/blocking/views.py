from rest_framework import generics

from blocking.models import BlockedUsers
from blocking.serializers import BlockedSerializer


class BlockedMixin(generics.GenericAPIView):
    queryset = BlockedUsers.objects.all()
    serializer_class = BlockedSerializer


class BlockedListCreateView(generics.ListCreateAPIView, BlockedMixin):
    pass


class BlockedDeleteView(generics.DestroyAPIView, BlockedMixin):
    lookup_field = 'pk'


blocked_list_create_view = BlockedListCreateView.as_view()
blocked_delete_view = BlockedDeleteView.as_view()
