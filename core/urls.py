from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Redirect root domain (/) to portal dashboard
    path('', lambda request: redirect('portal:dashboard')),
    
    # Use standard Django LoginView rendering your template
    path('login/', auth_views.LoginView.as_view(template_name='portal/login.html'), name='login'),
    
    # Main app routes
    path('admin/', admin.site.urls),
    path('portal/', include('portal.urls', namespace='portal')),
]