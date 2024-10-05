from django.urls import path, include

from api.views import api_root

urlpatterns = [
    path('', api_root, name="api-index"),
    path('users/', include('users.urls'), name="api-users"),
    path('auth/', include('rest_framework.urls'), name="api-auth"),
    # path('games/', include('games.urls'), name="api-games"),
]
