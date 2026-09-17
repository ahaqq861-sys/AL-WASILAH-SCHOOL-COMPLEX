from django.urls import path
from . import views

urlpatterns = [
    path('', views.portal_dashboard, name='portal_dashboard'),
    path('login/', views.custom_login, name='portal_login'),
    path('logout/', views.custom_logout, name='portal_logout'),
    path('grades/', views.student_grades, name='student_grades'),
    path('fees/', views.fee_statement, name='fee_statement'),
    path('students/', views.portal_dashboard, name='manage_students'),
    path('branding/', views.portal_dashboard, name='branding_settings'),
    path('report/<int:student_id>/', views.print_student_report, name='print_student_report'),
    path('receipt/<int:payment_id>/', views.print_fee_receipt, name='print_fee_receipt'),
    path('change-password/', views.change_password, name='change_password'),
]