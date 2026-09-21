from django.contrib import admin
from .models import SchoolBranding, AcademicClass, SubjectCourse, UserProfile, FeeLedger, TimetableEntry, AcademicEvent

@admin.register(SchoolBranding)
class SchoolBrandingAdmin(admin.ModelAdmin):
    list_display = ('school_name', 'current_academic_year', 'current_term')

@admin.register(FeeLedger)
class FeeLedgerAdmin(admin.ModelAdmin):
    list_display = ('student', 'academic_class', 'term', 'total_fees', 'amount_paid', 'balance_due')
    list_filter = ('academic_class', 'term')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'index_number', 'assigned_class')
    list_filter = ('role', 'assigned_class')

admin.site.register(AcademicClass)
admin.site.register(SubjectCourse)
admin.site.register(TimetableEntry)
admin.site.register(AcademicEvent)