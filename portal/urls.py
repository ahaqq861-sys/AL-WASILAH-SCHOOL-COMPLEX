from django.urls import path
from . import views

urlpatterns = [
    path('', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('students/', views.manage_students, name='manage_students'),
    path('teachers/', views.manage_teachers, name='manage_teachers'),
    
    # Student Navigation Routes
    path('assessment/', views.dashboard, name='student_assessment'),
    path('schedule/', views.dashboard, name='student_schedule'),
    path('attendance/', views.dashboard, name='student_attendance'),
]