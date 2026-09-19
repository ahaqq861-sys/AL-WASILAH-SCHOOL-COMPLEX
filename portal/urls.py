from django.urls import path
from . import views

app_name = 'portal'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.dashboard, name='portal_dashboard'),
    path('register-user/', views.register_user_view, name='register_user'),
    path('upload-results/', views.upload_results_view, name='upload_results'),
    path('upload-fees/', views.upload_fees_view, name='upload_fees'),
    path('record-payment/', views.record_payment_view, name='record_payment'),
    path('report-card/<int:student_id>/<int:term_id>/', views.report_card_view, name='report_card'),
    path('attendance/', views.attendance_view, name='attendance_view'),
    path('timetable/', views.timetable_view, name='timetable_view'),
    path('create-announcement/', views.create_announcement_view, name='create_announcement'),
    path('branding/', views.update_branding_view, name='update_branding'),
    path('profile/', views.profile_view, name='profile_view'),
    path('inbox/', views.inbox_view, name='inbox_view'),
    path('calendar/', views.calendar_view, name='calendar_view'),
    path('help/', views.help_view, name='help_view'),
    path('academics/', views.academics_view, name='academics_view'),
    path('finance/', views.finance_view, name='finance_view'),
    path('health/', views.health_view, name='health_view'),
    path('counselling/', views.counselling_view, name='counselling_view'),
]