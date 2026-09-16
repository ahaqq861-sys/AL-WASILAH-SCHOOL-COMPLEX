from django.contrib import admin
from .models import SchoolBranding


@admin.register(SchoolBranding)
class SchoolBrandingAdmin(admin.ModelAdmin):
    list_display = ("school_name", "tagline", "primary_color")