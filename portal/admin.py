from django.contrib import admin
from .models import TeacherProfile, ClassSection, Student, SubjectResult

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_id', 'department', 'phone_number')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'employee_id')
    list_filter = ('department',)

@admin.register(ClassSection)
class ClassSectionAdmin(admin.ModelAdmin):
    list_display = ('class_name', 'section_name', 'academic_year')
    search_fields = ('class_name', 'section_name', 'academic_year')
    list_filter = ('academic_year', 'class_name')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'first_name', 'last_name', 'current_class', 'gender', 'parent_phone')
    search_fields = ('student_id', 'first_name', 'last_name')
    list_filter = ('gender', 'current_class')

@admin.register(SubjectResult)
class SubjectResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject_name', 'class_score', 'exam_score', 'total_score', 'grade')
    search_fields = ('student__student_id', 'student__first_name', 'student__last_name', 'subject_name')
    list_filter = ('subject_name', 'grade')