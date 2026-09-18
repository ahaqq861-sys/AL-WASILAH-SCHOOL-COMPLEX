from django.contrib import admin
from .models import UserProfile, SchoolBranding, PendingModification

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone_number')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name')

@admin.register(SchoolBranding)
class SchoolBrandingAdmin(admin.ModelAdmin):
    list_display = ('school_name', 'logo_text', 'updated_at')

@admin.register(PendingModification)
class PendingModificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher', 'is_approved', 'created_at')
    list_filter = ('is_approved',)
    actions = ['approve_modifications']

    @admin.action(description='Approve selected modifications')
    def approve_modifications(self, request, queryset):
        queryset.update(is_approved=True)