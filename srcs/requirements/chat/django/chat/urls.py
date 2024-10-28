"""
URL configuration for chat project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from chat_messages.views import messages_view
from chats.views import chats_view, chat_view
from users.views import rename_user_view, delete_user_view

urlpatterns = [
    path('api/chat/', chats_view),
    path('api/chat/<int:pk>/', chat_view),
    path('api/chat/<int:pk>/messages/', messages_view),

    path('api/rename-user/<int:user_id>/', rename_user_view),
    path('api/delete-user/<int:user_id>/', delete_user_view),
]
