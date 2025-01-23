from lib_transcendence.permissions import NotGuest
from rest_framework import generics

from export_data.serializers import DownloadDataSerializer
from users.auth import get_user


class ExportDataView(generics.RetrieveAPIView):
    permission_classes = [NotGuest]
    serializer_class = DownloadDataSerializer

    def get_object(self):
        return get_user(self.request)

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, args, kwargs)
        file_name = f'user_{self.request.user.id}_data.json'
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


export_data_view = ExportDataView.as_view()
