from django.urls import path

from chat_messages.views import messages_view
from chats.views import chats_view, chat_view
from users.views import rename_user_view, block_user_view, delete_user_view

urlpatterns = [
    path('api/chat/', chats_view),
    path('api/chat/<int:pk>/', chat_view),
    path('api/chat/<int:pk>/messages/', messages_view),

    path('api/rename-user/<int:user_id>/', rename_user_view),
    path('api/block-user/<int:user_id>/<int:user_block>/', block_user_view), # todo move in library
    path('api/delete-user/<int:user_id>/', delete_user_view),
]
