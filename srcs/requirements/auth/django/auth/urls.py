from django.urls import path
from lib_transcendence.endpoints import Auth
from rest_framework_simplejwt.views import token_obtain_pair, token_refresh

from delete.views import delete_view
from guest.views import guest_token
from register.views import register_view
from update.views import update_view
from verify.views import token_verify

urlpatterns = [
    path(Auth.delete, delete_view),
    path(Auth.guest, guest_token),
    path(Auth.login, token_obtain_pair),
    path(Auth.refresh, token_refresh),
    path(Auth.register, register_view),
    path(Auth.update, update_view),
    path(Auth.verify, token_verify),
]
