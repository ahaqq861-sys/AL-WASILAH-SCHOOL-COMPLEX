from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('gradebook/', views.gradebook_view, name='gradebook'),
    path('fee-ledger/', views.fee_ledger_view, name='fee_ledger'),
]