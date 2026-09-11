from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import StudentProfile, TeacherProfile, SchoolBranding

def custom_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    branding = SchoolBranding.get_config()
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'portal/login.html', {'form': form, 'branding': branding})


def custom_logout(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    branding = SchoolBranding.get_config()
    return render(request, 'portal/dashboard.html', {'branding': branding})


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