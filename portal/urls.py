from django.urls import path
from . import views

urlpatterns = [
    path('', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Student Routes
    path('student/assessment/', views.student_assessment, name='student_assessment'),
    path('student/schedule/', views.student_schedule, name='student_schedule'),
    path('student/attendance/', views.student_attendance, name='student_attendance'),
    
    # Teacher Routes
    path('teacher/roster/', views.teacher_roster, name='teacher_roster'),
    path('teacher/grade-entry/', views.teacher_grade_entry, name='teacher_grade_entry'),
    
    # Admin Routes
    path('admin/students/', views.admin_students_db, name='admin_students'),
    path('admin/teachers/', views.admin_teachers_db, name='admin_teachers'),
    path('admin/create-user/', views.create_user_account, name='create_user'),
    path('admin/reset-password/', views.reset_user_password, name='reset_password'),
]