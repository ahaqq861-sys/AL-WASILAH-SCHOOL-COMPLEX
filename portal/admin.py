from django.contrib import admin
from .models import (
    SchoolBranding, UserProfile, AcademicClass, 
    Subject, Student, Grade, FeeLedger, Announcement
)

@admin.register(SchoolBranding)
class SchoolBrandingAdmin(admin.ModelAdmin):
    list_display = ('school_name', 'current_academic_year', 'current_term', 'contact_email')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('index_number', 'user', 'current_class', 'guardian_phone')
    search_fields = ('index_number', 'user__first_name', 'user__last_name')

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'academic_year', 'term', 'total_score')
    list_filter = ('academic_year', 'term', 'subject')

@admin.register(FeeLedger)
class FeeLedgerAdmin(admin.ModelAdmin):
    list_display = ('student', 'academic_year', 'term', 'total_amount', 'amount_paid', 'balance', 'status')
    list_filter = ('academic_year', 'term')

admin.site.register(UserProfile)
admin.site.register(AcademicClass)
admin.site.register(Subject)
admin.site.register(Announcement)