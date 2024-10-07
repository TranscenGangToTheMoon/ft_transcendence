from django.urls import path, re_path
from landing import views

urlpatterns = [
    path('', views.landing, name='index'),
    re_path(r'^(.*/)?login/$', views.login, name='login'),
    path('test/', views.test, name='test'),
]
