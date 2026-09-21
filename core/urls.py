from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from portal import views as portal_views  # Imports portal views directly

urlpatterns = [
    # Redirect root domain (/) to portal dashboard
    path('', lambda request: redirect('portal:dashboard')),
    
    # Direct /login/ path to the portal login view
    path('login/', portal_views.login_view, name='login'),
    
    # Main app routes
    path('admin/', admin.site.urls),
    path('portal/', include('portal.urls', namespace='portal')),
]