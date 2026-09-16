from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import SchoolBranding, StudentProfile, TeacherProfile


class TeacherProfileInline(admin.StackedInline):
    model = TeacherProfile
    can_delete = False
    verbose_name_plural = "Teacher Profile"


class StudentProfileInline(admin.StackedInline):
    model = StudentProfile
    can_delete = False
    verbose_name_plural = "Student Profile"


class UserAdmin(BaseUserAdmin):
    inlines = (TeacherProfileInline, StudentProfileInline)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(SchoolBranding)
class SchoolBrandingAdmin(admin.ModelAdmin):
    list_display = (
        "school_name",
        "phone_number",
        "email_address",
        "primary_color",
    )

    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)