from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

urlpatterns = [
    # Redirect root URL to admin panel
    path('', RedirectView.as_view(url='/admin/', permanent=False)),

    # Django Admin Panel
    path('admin/', admin.site.urls),

    # Main Portal Frontend URLs
    path('portal/', include('portal.urls')),

    # Serve media files on production server
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)