from django.contrib import admin
from .models import SchoolBranding, TeacherProfile, StudentProfile

@admin.register(SchoolBranding)
class SchoolBrandingAdmin(admin.ModelAdmin):
    list_display = ('school_name', 'phone_number', 'email_address', 'primary_color')
    
    def has_add_permission(self, request):
        # Prevent creating multiple config rows
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'user', 'assigned_class', 'subject_specialization')
    search_fields = ('employee_id', 'user__username', 'user__first_name', 'user__last_name')

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'user', 'current_class', 'guardian_contact')
    search_fields = ('student_id', 'user__username', 'user__first_name', 'user__last_name')