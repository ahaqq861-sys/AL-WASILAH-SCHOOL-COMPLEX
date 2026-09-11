from django.urls import path
from . import views

urlpatterns = [
    path('', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin/create-user/', views.create_user_account, name='create_user'),
    path('admin/reset-password/', views.reset_user_password, name='reset_password'),
]