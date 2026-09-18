from django.contrib import admin
from .models import ClassLevel, AcademicTerm, StudentProfile, TeacherProfile, Grade, FeeRecord

@admin.action(description="Promote selected students to the next class level")
def promote_students(modeladmin, request, queryset):
    promoted_count = 0
    graduated_count = 0
    for student in queryset:
        if student.current_class and student.current_class.next_class:
            student.current_class = student.current_class.next_class
            student.save()
            promoted_count += 1
        elif student.current_class and not student.current_class.next_class:
            student.is_graduated = True
            student.save()
            graduated_count += 1
    modeladmin.message_user(request, f"Successfully promoted {promoted_count} students. {graduated_count} marked as graduated.")

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'user', 'current_class', 'is_graduated')
    list_filter = ('current_class', 'is_graduated')
    actions = [promote_students]

admin.site.register(ClassLevel)
admin.site.register(AcademicTerm)
admin.site.register(TeacherProfile)
admin.site.register(Grade)
admin.site.register(FeeRecord)