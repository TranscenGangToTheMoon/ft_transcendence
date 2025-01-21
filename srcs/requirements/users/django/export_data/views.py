from lib_transcendence.permissions import NotGuest
from rest_framework import generics

from export_data.serializers import DownloadDataSerializer
from users.auth import get_user


class ExportDataView(generics.RetrieveAPIView):
    permission_classes = [NotGuest]
    serializer_class = DownloadDataSerializer

    def get_object(self):
        return get_user(self.request)


export_data_view = ExportDataView.as_view()
