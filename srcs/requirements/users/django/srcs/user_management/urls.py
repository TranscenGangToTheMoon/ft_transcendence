from django.urls import path

from users.views import users_me_view

urlpatterns = [
    path('api/users/me/', users_me_view, name='users_view'), # todo : DELETE | UPDATE check again the password
    # path('api/users/me/friends/', users, name='users'), # todo : make GET, POST, UPDATE - get friends, send friend request, accept_friend_request, etc...
    # path('api/users/me/blocked/', users, name='users'), # todo : make GET, POST, UPDATE
    # path('api/users/me/profile_picture/', users, name='users'), # todo : make POST, UPDATE
    # path('api/users/me/online_status/', users, name='users'), # todo : UPDATE is_online game_playing last_online
    # path('api/users/me/coins/', users, name='users'), # todo : UPDATE only transcendence-nw
    # path('api/users/me/trophy/', users, name='users'), # todo : UPDATE only transcendence-nw
    # path('api/users/me/rank/', users, name='users'), # todo : UPDATE only transcendence-nw
    # path('api/users/<int:pk>/', users, name='users'), # todo : make GET
]
