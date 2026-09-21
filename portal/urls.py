from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register_user, name='register_user'),
    path('fee-ledger/<int:ledger_id>/edit/', views.edit_fee_ledger, name='edit_fee_ledger'),
]