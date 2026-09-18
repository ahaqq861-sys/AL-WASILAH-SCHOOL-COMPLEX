from django.contrib import admin
from .models import ClassLevel, AcademicTerm, TeacherProfile, StudentProfile, Grade, FeeRecord

@admin.register(ClassLevel)
class ClassLevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    ordering = ('order',)

@admin.register(AcademicTerm)
class AcademicTermAdmin(admin.ModelAdmin):
    list_display = ('year', 'trimester', 'is_active')
    list_filter = ('is_active', 'trimester')

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('staff_id', 'full_name', 'assigned_class', 'phone_number')
    search_fields = ('staff_id', 'full_name')

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'full_name', 'current_class', 'gender', 'is_promoted')
    list_filter = ('current_class', 'gender', 'is_promoted')
    search_fields = ('student_id', 'full_name')

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'term', 'class_score', 'exam_score', 'total_score', 'grade')
    list_filter = ('term', 'subject', 'grade')
    search_fields = ('student__full_name', 'student__student_id', 'subject')

@admin.register(FeeRecord)
class FeeRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'term', 'amount_due', 'amount_paid', 'balance')
    list_filter = ('term',)
    search_fields = ('student__full_name', 'student__student_id')