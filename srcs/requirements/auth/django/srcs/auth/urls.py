from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import token_obtain_pair, token_refresh, token_verify

from guest.views import guest_token, guest_register
from register.views import register

urlpatterns = [
    path('api/auth/guest/', guest_token, name="api-guest-token"),
    path('api/auth/guest/register/', guest_register, name="api-guest-register"),
    path('api/auth/register/', register, name='api-register'),
    path('api/auth/token/', token_obtain_pair, name='api-token-obtain-pair'),
    path('api/auth/token/refresh', token_refresh, name='api-token-refresh'),
    path('api/auth/token/verify/', token_verify, name='api-token-verify'),
    path('auth/admin/', admin.site.urls),
]
