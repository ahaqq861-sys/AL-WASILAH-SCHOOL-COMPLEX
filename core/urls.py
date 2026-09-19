from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('portal/', include('portal.urls', namespace='portal')),
    path('', include('portal.urls')),  # Redirects root URL directly to portal views
]