from django.urls import path
from . import views

app_name = 'portal'

urlpatterns = [
    path('', views.dashboard, name='portal_dashboard'),
    path('students/', views.student_directory, name='student_directory'),
    path('grades/', views.grade_portal, name='grade_portal'),
    path('fees/', views.fee_admin, name='fee_admin'),
    path('promotion/', views.promotion_management, name='promotion_management'),
]