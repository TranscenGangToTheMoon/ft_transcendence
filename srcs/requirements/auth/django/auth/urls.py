from django.urls import path
from lib_transcendence.endpoints import Auth
from rest_framework_simplejwt.views import token_obtain_pair as obtain_login_token_view
from rest_framework_simplejwt.views import token_refresh as refresh_token_view

from delete.views import delete_user_view
from guest.views import optain_guest_token_view
from register.views import register_view, register_guest_view
from update.views import update_user_view
from verify.views import verify_token_view

urlpatterns = [
    path(Auth.guest, optain_guest_token_view),
    path(Auth.register, register_view),
    path(Auth.register_guest, register_guest_view),

    path(Auth.login, obtain_login_token_view),

    path(Auth.update, update_user_view),
    path(Auth.delete, delete_user_view),

    path(Auth.refresh, refresh_token_view),
    path(Auth.verify, verify_token_view),
]
