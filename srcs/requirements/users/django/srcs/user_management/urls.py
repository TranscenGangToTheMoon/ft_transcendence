from django.urls import path

from users.views import users_me

urlpatterns = [
    path('api/users/me/', users_me, name='users_me'),
]
