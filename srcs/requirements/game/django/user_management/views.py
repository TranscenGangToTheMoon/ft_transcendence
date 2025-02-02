from rest_framework import generics

from user_management.serializers import DownloadDataSerializer, RetrieveUserPlaceSerializer


class RetrieveUserPlaceView(generics.RetrieveAPIView):
    serializer_class = RetrieveUserPlaceSerializer

    def get_object(self):
        return self.kwargs['user_id']


class DownloadDataView(generics.RetrieveAPIView):
    serializer_class = DownloadDataSerializer
    paginattion_class = None

    def get_object(self):
        return self.kwargs['user_id']


retrieve_user_place_view = RetrieveUserPlaceView.as_view()
export_data_view = DownloadDataView.as_view()
