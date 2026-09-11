from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SchoolBranding, TeacherProfile, StudentProfile

def custom_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    branding = SchoolBranding.get_config()

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if role == 'admin' and not (user.is_superuser or user.is_staff):
                messages.error(request, "Access Denied: Account lacks Administrative privileges.")
                return render(request, 'portal/login.html', {'branding': branding})

            login(request, user)
            request.session['selected_role'] = role
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password credentials.")

    return render(request, 'portal/login.html', {'branding': branding})


def custom_logout(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    branding = SchoolBranding.get_config()
    role = request.session.get('selected_role')

    if not role:
        if request.user.is_superuser or request.user.is_staff:
            role = 'admin'
        elif hasattr(request.user, 'teacher_profile'):
            role = 'teacher'
        else:
            role = 'student'

    # Statistics for Admin Portal Dashboard
    total_students = StudentProfile.objects.count()
    total_teachers = TeacherProfile.objects.count()

    context = {
        'user': request.user,
        'role': role,
        'branding': branding,
        'total_students': total_students,
        'total_teachers': total_teachers,
    }

    if role == 'admin':
        return render(request, 'portal/admin_dashboard.html', context)
    elif role == 'teacher':
        return render(request, 'portal/teacher_dashboard.html', context)
    else:
        return render(request, 'portal/student_dashboard.html', context)


@login_required
def create_user_account(request):
    """Admin function to provision new teacher or student login credentials."""
    if not (request.user.is_superuser or request.user.is_staff):
        messages.error(request, "Unauthorized access.")
        return redirect('dashboard')

    if request.method == 'POST':
        account_type = request.POST.get('account_type')
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        id_code = request.POST.get('id_code')
        class_assignment = request.POST.get('class_assignment', '')

        if User.objects.filter(username=username).exists():
            messages.error(request, f"Username '{username}' already exists.")
            return redirect('dashboard')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        if account_type == 'teacher':
            TeacherProfile.objects.create(user=user, employee_id=id_code, assigned_class=class_assignment)
            messages.success(request, f"Teacher account '{username}' successfully created!")
        else:
            StudentProfile.objects.create(user=user, student_id=id_code, current_class=class_assignment)
            messages.success(request, f"Student account '{username}' successfully created!")

    return redirect('dashboard')


@login_required
def reset_user_password(request):
    """Admin function to reset passwords for students and teachers."""
    if not (request.user.is_superuser or request.user.is_staff):
        messages.error(request, "Unauthorized access.")
        return redirect('dashboard')

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        new_password = request.POST.get('new_password')

        target_user = get_object_or_404(User, id=user_id)
        target_user.set_password(new_password)
        target_user.save()

        messages.success(request, f"Password successfully updated for user '{target_user.username}'.")

    return redirect('dashboard')