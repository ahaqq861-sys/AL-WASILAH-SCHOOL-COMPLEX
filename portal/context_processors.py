from .models import SchoolBranding

def school_branding(request):
    branding, _ = SchoolBranding.objects.get_or_create(
        id=1,
        defaults={
            "school_name": "Al-Wasilah School Complex",
            "tagline": "Knowledge and Virtue",
            "primary_color": "#800020",
            "secondary_color": "#1A252C"
        }
    )
    return {"branding": branding}