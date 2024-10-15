from django.urls import path

from block.views import block_list_create_view, block_delete_view
from friend_requests.views import friend_requests_list_create_view, friend_requests_delete_view, \
    friend_requests_receive_list_view
from friends.views import friends_list_create_view, friends_delete_view
from users.views import users_me_view, user_retrieve_view

urlpatterns = [
    path('api/users/me/', users_me_view, name='users_view'),
    path('api/users/<int:pk>/', user_retrieve_view, name='api-user-retrieve'),

    path('api/users/me/friends/', friends_list_create_view, name='api-friend-create-list'),
    path('api/users/me/friends/<int:pk>/', friends_delete_view, name='api-friend-delete'),
    path('api/users/me/friend_requests/', friend_requests_list_create_view, name='api-friend-request-create-list'),
    path('api/users/me/friend_requests/receive/', friend_requests_receive_list_view, name='api-friend-request-receive-list'),
    path('api/users/me/friend_requests/<int:pk>/', friend_requests_delete_view, name='api-friend-request-delete'),

    path('api/users/me/block/', block_list_create_view, name='api-block-list-update'),
    path('api/users/me/block/<int:pk>/', block_delete_view, name='api-block-delete'),

    # path('api/users/me/profile_picture/', users, name='users'), # todo : make POST, UPDATE
    # path('api/users/me/online_status/', users, name='users'), # todo : UPDATE is_online game_playing last_online by notif service
    # path('api/users/me/coins/', users, name='users'), # todo : UPDATE only transcendence-nw / game service
    # path('api/users/me/trophy/', users, name='users'), # todo : UPDATE only transcendence-nw / game service
    # path('api/users/me/rank/', users, name='users'), # todo : UPDATE only transcendence-nw / game service
]
