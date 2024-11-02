from django.urls import path

from block.views import block_list_create_view, block_delete_view
from friend_requests.views import friend_requests_list_create_view, friend_requests_delete_view, \
    friend_requests_receive_list_view
from friends.views import friends_list_create_view, friends_delete_view
from users.views import users_me_view, user_retrieve_view
from validate.views import validate_chat_view

urlpatterns = [
    path('api/users/me/', users_me_view, name='api-users-me-retrieve'),
    path('api/users/<int:pk>/', user_retrieve_view, name='api-user-retrieve'),

    path('api/users/me/friends/', friends_list_create_view, name='api-friend-create-list'),
    path('api/users/me/friends/<int:pk>/', friends_delete_view, name='api-friend-delete'),
    path('api/users/me/friend_requests/', friend_requests_list_create_view, name='api-friend-request-create-list'),
    path('api/users/me/friend_requests/receive/', friend_requests_receive_list_view, name='api-friend-request-receive-list'),
    path('api/users/me/friend_requests/<int:pk>/', friend_requests_delete_view, name='api-friend-request-delete'),

    path('api/users/me/block/', block_list_create_view, name='api-block-list-update'),
    path('api/users/me/block/<int:pk>/', block_delete_view, name='api-block-delete'),

    path('api/validate/chat/', validate_chat_view, name='api-validate-chat'),
]
