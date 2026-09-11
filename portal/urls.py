from django.urls import path
from . import views

urlpatterns = [
    # Authentication Routes
    path('', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),

    # Core Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Directory & User Management Routes
    path('students/', views.manage_students, name='manage_students'),
    path('teachers/', views.manage_teachers, name='manage_teachers'),
]