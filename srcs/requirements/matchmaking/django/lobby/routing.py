from django.urls import re_path
from . import customer

websocket_urlpatterns = [
	re_path('lobby/', customer.customer.as_asgi()),
]
