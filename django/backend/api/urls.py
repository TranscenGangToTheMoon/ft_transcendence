from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

from api.views import api_root

urlpatterns = [
    path('', api_root, name="api-index"),
    path('users/', include('users.urls'), name="api-users"),
    path('auth/', obtain_auth_token, name="api-auth"),
    # path('games/', include('games.urls'), name="api-games"),
]
