from rest_framework import generics

from user_management.serializers import DownloadDataSerializer


class DownloadDataView(generics.RetrieveAPIView):
    serializer_class = DownloadDataSerializer
    paginattion_class = None

    def get_object(self):
        return self.kwargs['user_id']


export_data_view = DownloadDataView.as_view()
