from .models import SchoolBranding

def site_branding(request):
    branding = SchoolBranding.objects.first()
    return {'branding': branding}