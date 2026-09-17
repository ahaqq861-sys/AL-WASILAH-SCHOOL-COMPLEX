from django.contrib import admin
from .models import SchoolBranding, UserProfile, StudentGrade, FeePayment

@admin.register(SchoolBranding)
class SchoolBrandingAdmin(admin.ModelAdmin):
    list_display = ('school_name', 'primary_color', 'phone_number', 'email_address')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name')

@admin.register(StudentGrade)
class StudentGradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'score', 'term', 'date_recorded')
    list_filter = ('term', 'subject')
    search_fields = ('student__username', 'subject')

@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = ('student', 'amount_paid', 'total_fee', 'balance', 'date_paid')
    search_fields = ('student__username',)