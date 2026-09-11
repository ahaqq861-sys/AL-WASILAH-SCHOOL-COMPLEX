from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django Admin Interface
    path('admin/', admin.site.urls),

    # Include routes from your portal app
    # (If your portal app has its own urls.py)
    path('', include('portal.urls')),
]

# Serve static and media files during development & production fallback
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)