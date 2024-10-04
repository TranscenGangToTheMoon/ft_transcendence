from django.http import HttpResponse
from django.urls import path

from api.views import api_root

urlpatterns = [
    path('', api_root, name="main"),
    path('user/', api_root, name="main"),
]
