from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    # Redirect root domain (/) directly to the portal dashboard
    path('', lambda request: redirect('portal:dashboard')),
    path('admin/', admin.site.urls),
    path('portal/', include('portal.urls', namespace='portal')),
]