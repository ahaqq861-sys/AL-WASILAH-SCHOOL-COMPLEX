from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import CustomLoginView, dashboard

urlpatterns = [
    path('', dashboard, name='index'),
    path('portal/', dashboard, name='dashboard'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
]