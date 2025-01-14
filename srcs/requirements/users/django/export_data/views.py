import json
import os
import threading
import time

from django.conf import settings
from django.http import FileResponse
from lib_transcendence.permissions import NotGuest
from rest_framework import generics

from export_data.serializers import DownloadDataSerializer
from users.auth import get_user


class ExportDataView(generics.RetrieveAPIView): # todo test
    permission_classes = [NotGuest]
    serializer_class = DownloadDataSerializer

    def get_object(self):
        return get_user(self.request)

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, args, kwargs)
        print(response.data, flush=True)
        print(type(response.data), flush=True)

        file_name = f'user_{self.request.user.id}_data.json'
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)

        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(response.data, json_file, indent=4, ensure_ascii=False)

        response = FileResponse(open(file_path, 'rb'), content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        threading.Thread(target=remove_file, args=(file_path, )).start()
        return response


def remove_file(file_path):
    time.sleep(2)
    os.remove(file_path)


# class ExportDataView(generics.RetrieveAPIView):
#     permission_classes = [NotGuest]
#     serializer_class = DownloadDataSerializer
#
#     def get_object(self):
#         return get_user(self.request)


export_data_view = ExportDataView.as_view()
