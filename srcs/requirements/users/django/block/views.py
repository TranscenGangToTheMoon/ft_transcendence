from rest_framework import generics

from block.models import Block
from block.serializers import BlockSerializer


class BlockMixin(generics.GenericAPIView):
    queryset = Block.objects.all()
    serializer_class = BlockSerializer


class BlockListCreateView(generics.ListCreateAPIView, BlockMixin):
    pass


class BlockDeleteView(generics.DestroyAPIView, BlockMixin):
    lookup_field = 'pk'


block_list_create_view = BlockListCreateView.as_view()
block_delete_view = BlockDeleteView.as_view()
