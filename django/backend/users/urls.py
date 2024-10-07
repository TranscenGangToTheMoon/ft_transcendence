from django.urls import path

from users.views import users_retrieve_update_delete_view, users_list_create_view, users_retrieve_view

urlpatterns = [
    path('', users_list_create_view, name="users-list"),
    path('<int:pk>/', users_retrieve_view, name="users-detail"),
    path('me/', users_retrieve_update_delete_view, name="users-me"),
]
