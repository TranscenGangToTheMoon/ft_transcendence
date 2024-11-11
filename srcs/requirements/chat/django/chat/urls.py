from django.urls import path
from lib_transcendence.endpoints import Chat, UsersManagement

from chat_messages.views import messages_view
from chats.views import chats_view, chat_view
from users.views import rename_user_view, blocked_user_view, delete_user_view

urlpatterns = [
    path(Chat.chats, chats_view),
    path(Chat.chat, chat_view),
    path(Chat.messages, messages_view),

    path(UsersManagement.rename_user, rename_user_view),
    path(UsersManagement.blocked_user, blocked_user_view),
    path(UsersManagement.delete_user, delete_user_view),
]
