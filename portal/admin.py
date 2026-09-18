from django.contrib import admin
from .models import Student, Grade

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'name', 'student_class', 'gender', 'fees_due', 'fees_paid', 'promoted')
    search_fields = ('student_id', 'name', 'student_class')
    list_filter = ('student_class', 'gender', 'promoted')

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'trimester', 'class_score', 'exam_score', 'total_score', 'grade')
    search_fields = ('student__name', 'student__student_id', 'subject')
    list_filter = ('trimester', 'subject', 'grade')