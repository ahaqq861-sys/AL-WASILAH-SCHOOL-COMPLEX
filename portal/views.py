from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import StudentProfile, TeacherProfile, SchoolBranding

@login_required
def manage_students(request):
    branding = SchoolBranding.get_config()
    try:
        students = StudentProfile.objects.select_related('user').all().order_by('current_class', 'user__first_name')
    except Exception:
        students = []

    context = {
        'branding': branding,
        'students': students,
    }
    return render(request, 'portal/manage_students.html', context)


@login_required
def manage_teachers(request):
    branding = SchoolBranding.get_config()
    try:
        teachers = TeacherProfile.objects.select_related('user').all().order_by('user__first_name')
    except Exception:
        teachers = []

    context = {
        'branding': branding,
        'teachers': teachers,
    }
    return render(request, 'portal/manage_teachers.html', context)