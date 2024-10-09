from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from api.views import api_root

urlpatterns = [
    path('', api_root, name="api-index"),
    path('users/', include('users.urls'), name="api-users"),
    path('auth/', obtain_auth_token, name="api-auth"),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    # path('games/', include('games.urls'), name="api-games"),
]
