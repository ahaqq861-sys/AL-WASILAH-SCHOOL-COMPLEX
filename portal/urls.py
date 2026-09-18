from django.urls import path
from . import views

app_name = 'portal'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.dashboard, name='portal_dashboard'),
    path('register-user/', views.register_user_view, name='register_user'),
    path('branding/', views.update_branding_view, name='update_branding'),
    path('submit-mod/', views.submit_modification_view, name='submit_mod'),
    path('approve-mod/<int:mod_id>/', views.approve_modification_view, name='approve_mod'),
    path('profile/', views.profile_view, name='profile_view'),
    path('inbox/', views.inbox_view, name='inbox_view'),
    path('calendar/', views.calendar_view, name='calendar_view'),
    path('help/', views.help_view, name='help_view'),
    path('academics/', views.academics_view, name='academics_view'),
    path('finance/', views.finance_view, name='finance_view'),
    path('health/', views.health_view, name='health_view'),
    path('counselling/', views.counselling_view, name='counselling_view'),
]