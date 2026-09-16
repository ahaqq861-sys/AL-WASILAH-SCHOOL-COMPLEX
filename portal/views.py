import random
import string
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib import messages
from .models import UserProfile, SchoolBranding

def get_branding():
    return SchoolBranding.objects.first() or SchoolBranding.objects.create()

def custom_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            profile, _ = UserProfile.objects.get_or_create(user=user)
            if profile.must_change_password:
                return redirect('change_password')
            return redirect('dashboard')
    else:
        form = AuthenticationForm()

    return render(request, 'portal/login.html', {'form': form, 'branding': get_branding()})

@login_required
def custom_logout(request):
    logout(request)
    return redirect('login')

@login_required
def change_password(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            profile.must_change_password = False
            profile.save()
            messages.success(request, 'Your password was successfully updated!')
            return redirect('dashboard')
    else:
        form = PasswordChangeForm(request.user)
        
    return render(request, 'portal/change_password.html', {
        'form': form,
        'branding': get_branding(),
        'profile': profile
    })

@login_required
def dashboard(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if profile.must_change_password:
        return redirect('change_password')

    context = {
        'branding': get_branding(),
        'profile': profile
    }

    if profile.role == 'admin' or request.user.is_superuser:
        return render(request, 'portal/admin_dashboard.html', context)
    elif profile.role == 'teacher':
        return render(request, 'portal/teacher_dashboard.html', context)
    else:
        return render(request, 'portal/student_dashboard.html', context)

@login_required
def manage_students(request):
    if request.method == 'POST' and 'create_student' in request.POST:
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        student_id = request.POST.get('student_id', '').strip()
        current_class = request.POST.get('current_class', '').strip()
        guardian_contact = request.POST.get('guardian_contact', '').strip()
        temp_pass = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

        if User.objects.filter(username=student_id).exists():
            messages.error(request, f"Student ID '{student_id}' already exists.")
        else:
            user = User.objects.create_user(username=student_id, password=temp_pass, first_name=first_name, last_name=last_name)
            UserProfile.objects.create(user=user, role='student', student_id=student_id, current_class=current_class, guardian_contact=guardian_contact, must_change_password=True)
            messages.success(request, f"Student created. Temp password: {temp_pass}")
            return redirect('manage_students')

    students = UserProfile.objects.filter(role='student')
    return render(request, 'portal/manage_students.html', {'students': students, 'branding': get_branding()})

@login_required
def manage_teachers(request):
    if request.method == 'POST' and 'create_teacher' in request.POST:
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').strip()
        subject = request.POST.get('subject', '').strip()
        temp_pass = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

        if User.objects.filter(username=username).exists():
            messages.error(request, f"Teacher username '{username}' already exists.")
        else:
            user = User.objects.create_user(username=username, password=temp_pass, first_name=first_name, last_name=last_name)
            UserProfile.objects.create(user=user, role='teacher', subject_assigned=subject, must_change_password=True)
            messages.success(request, f"Teacher account created. Temp password: {temp_pass}")
            return redirect('manage_teachers')

    teachers = UserProfile.objects.filter(role='teacher')
    return render(request, 'portal/manage_teachers.html', {'teachers': teachers, 'branding': get_branding()})

@login_required
def student_assessment(request):
    return render(request, 'portal/student_assessment.html', {'branding': get_branding()})

@login_required
def student_schedule(request):
    return render(request, 'portal/student_schedule.html', {'branding': get_branding()})

@login_required
def student_attendance(request):
    return render(request, 'portal/student_attendance.html', {'branding': get_branding()})