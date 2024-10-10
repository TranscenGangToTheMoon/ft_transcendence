from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import token_obtain_pair, token_refresh

from guest.views import guest_token, register
from verify.views import token_verify

urlpatterns = [
    path('api/auth/guest/', guest_token, name="api-guest-token"),
    path('api/auth/register/', register, name='api-register'), #todo : create own app
    path('api/auth/token/', token_obtain_pair, name='api-token-obtain-pair'),
    path('api/auth/refresh', token_refresh, name='api-token-refresh'),
    path('api/auth/verify/', token_verify, name='api-token-verify'),
    path('auth/admin/', admin.site.urls),
]
