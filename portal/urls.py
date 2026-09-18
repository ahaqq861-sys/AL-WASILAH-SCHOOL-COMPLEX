from django.urls import path
from . import views

app_name = 'portal'

urlpatterns = [
    path('', views.dashboard, name='portal_dashboard'),
    path('profile/', views.profile_view, name='profile_view'),
    path('inbox/', views.inbox_view, name='inbox_view'),
    path('calendar/', views.calendar_view, name='calendar_view'),
    path('help/', views.help_view, name='help_view'),
    path('academics/', views.academics_view, name='academics_view'),
    path('accommodation/', views.accommodation_view, name='accommodation_view'),
    path('finance/', views.finance_view, name='finance_view'),
    path('health/', views.health_view, name='health_view'),
    path('counselling/', views.counselling_view, name='counselling_view'),
]