from django.urls import path
from . import views

urlpatterns = [
    path('', views.portal_dashboard, name='portal_dashboard'),
    path('login/', views.custom_login, name='portal_login'),
    path('logout/', views.custom_logout, name='portal_logout'),
    path('change-password/', views.change_password, name='change_password'),
]