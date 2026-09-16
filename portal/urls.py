from django.urls import path
from . import views

urlpatterns = [
    path('', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('change-password/', views.change_password, name='change_password'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Admin Routes
    path('manage-students/', views.manage_students, name='manage_students'),
    path('manage-teachers/', views.manage_teachers, name='manage_teachers'),
    
    # Student Routes
    path('assessment/', views.student_assessment, name='student_assessment'),
    path('schedule/', views.student_schedule, name='student_schedule'),
    path('attendance/', views.student_attendance, name='student_attendance'),
]