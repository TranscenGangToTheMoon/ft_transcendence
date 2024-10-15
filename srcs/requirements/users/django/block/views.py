from rest_framework import generics

from block.models import Block
from block.serializers import BlockSerializer


class FriendRequestsMixin(generics.GenericAPIView):
    queryset = Block.objects.all()
    serializer_class = BlockSerializer


class BlockListCreateView(generics.ListCreateAPIView, FriendRequestsMixin):
    pass


class BlockDeleteView(generics.DestroyAPIView, FriendRequestsMixin):
    lookup_field = 'pk'


block_list_create_view = BlockListCreateView.as_view()
block_delete_view = BlockDeleteView.as_view()
