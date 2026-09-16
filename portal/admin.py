from django.contrib import admin
from .models import UserProfile, SchoolBranding

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'student_id', 'current_class', 'subject_assigned', 'must_change_password')
    list_filter = ('role', 'must_change_password')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'student_id')

@admin.register(SchoolBranding)
class SchoolBrandingAdmin(admin.ModelAdmin):
    list_display = ('school_name', 'primary_color')