from django.urls import path
from rest_framework_simplejwt.views import token_obtain_pair, token_refresh

from delete.views import delete_view
from guest.views import guest_token
from register.views import register_view
from update.views import update_view
from verify.views import token_verify

urlpatterns = [
    path('api/auth/guest/', guest_token, name="api-auth-guest-token"),
    path('api/auth/update/', update_view, name='api-auth-update-user'),
    path('api/auth/delete/', delete_view, name='api-auth-delete-user'),
    path('api/auth/register/', register_view, name='api-auth-register'),
    path('api/auth/login/', token_obtain_pair, name='api-auth-login'),
    path('api/auth/refresh/', token_refresh, name='api-auth-token-refresh'),
    path('api/auth/verify/', token_verify, name='api-auth-token-verify'), # todo change to verify
]
