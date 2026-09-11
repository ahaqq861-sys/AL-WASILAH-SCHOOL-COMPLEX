from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

urlpatterns = [
    # Clicking "Visit site" or going to / now opens the portal dashboard
    path('', RedirectView.as_view(url='/portal/dashboard/', permanent=False)),

    # Django Admin Panel
    path('admin/', admin.site.urls),

    # Main Portal Frontend URLs
    path('portal/', include('portal.urls')),

    # Serve uploaded media files
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)