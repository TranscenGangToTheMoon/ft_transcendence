from django.urls import path

from users.views import user_index, UsersDetailView, UsersCreateView, UsersListDetailView, UsersUpdateView, \
    UsersDeleteView, UsersMixinView

urlpatterns = [
    # path('', user_index, name="api-users-index"),
    path('', UsersCreateView.as_view(), name="api-users-create"),
    path('<int:pk>/', UsersMixinView.as_view(), name="api-users-details"),
    path('<int:pk>/update', UsersUpdateView.as_view(), name="api-users-update"),
    path('<int:pk>/delete', UsersDeleteView.as_view(), name="api-users-delete"),
    path('all/', UsersListDetailView.as_view(), name="api-users-details"),
]
