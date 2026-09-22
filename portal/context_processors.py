from .models import SchoolBranding

def site_branding(request):
    branding = SchoolBranding.objects.first()
    if not branding:
        branding = SchoolBranding.objects.create()
    return {
        'site_branding': branding
    }