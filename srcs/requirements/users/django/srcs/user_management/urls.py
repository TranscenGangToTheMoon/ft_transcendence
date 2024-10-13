from django.urls import path

from friends.views import friends_view
from users.views import users_me_view

urlpatterns = [
    path('api/users/me/', users_me_view, name='users_view'),
    # todo : make two url friend, and friend request
    #  - GET all friends
    #  - DELETE friends
    #  - POST friend request
    #  - DELETE friend request
    #  - GET all friend request
    #  - POST accept friend request
    path('api/users/me/friends/', friends_view, name='users'),
    # path('api/users/me/friends/<int:pk>/', friends_view, name='users'), # todo : DELETE
    # path('api/users/me/blocked/', users, name='users'), # todo : make GET, POST, UPDATE \\ when block remove friend request
    # path('api/users/me/profile_picture/', users, name='users'), # todo : make POST, UPDATE
    # path('api/users/me/online_status/', users, name='users'), # todo : UPDATE is_online game_playing last_online
    # path('api/users/me/coins/', users, name='users'), # todo : UPDATE only transcendence-nw
    # path('api/users/me/trophy/', users, name='users'), # todo : UPDATE only transcendence-nw
    # path('api/users/me/rank/', users, name='users'), # todo : UPDATE only transcendence-nw
    # path('api/users/<int:pk>/', users, name='users'), # todo : make GET
]
