from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile, StudentGrade, FeePayment, SchoolBranding

def get_user_role(user):
    profile, _ = UserProfile.objects.get_or_create(
        user=user,
        defaults={'role': 'admin' if user.is_superuser else 'student'}
    )
    return profile.role

def custom_login(request):
    if request.user.is_authenticated:
        return redirect('portal_dashboard')

    branding, _ = SchoolBranding.objects.get_or_create(id=1)

    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            profile, _ = UserProfile.objects.get_or_create(user=user)
            if profile.is_first_login:
                messages.warning(request, 'First-time login detected. Please change your default password.')
                return redirect('first_time_password_change')
            return redirect('portal_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'portal/login.html', {'branding': branding})

def custom_logout(request):
    logout(request)
    return redirect('portal_login')

@login_required
def first_time_password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            profile = request.user.userprofile
            profile.is_first_login = False
            profile.save()
            messages.success(request, 'Password updated successfully! Welcome to your portal.')
            return redirect('portal_dashboard')
        else:
            messages.error(request, 'Please fix errors below.')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'portal/first_time_password.html', {'form': form})

@login_required
def portal_dashboard(request):
    if request.user.userprofile.is_first_login:
        return redirect('first_time_password_change')

    role = get_user_role(request.user)
    branding, _ = SchoolBranding.objects.get_or_create(id=1)
    context = {'role': role, 'branding': branding}

    if role == 'admin':
        context['total_students'] = UserProfile.objects.filter(role='student').count()
        context['total_teachers'] = UserProfile.objects.filter(role='teacher').count()
    elif role == 'student':
        context['grades'] = StudentGrade.objects.filter(student=request.user)
        context['payments'] = FeePayment.objects.filter(student=request.user)

    return render(request, 'portal/dashboard.html', context)

@login_required
def manage_students(request):
    if request.user.userprofile.is_first_login:
        return redirect('first_time_password_change')

    role = get_user_role(request.user)

    # Register New Teacher / Student with Default Password '123456'
    if request.method == 'POST' and role == 'admin':
        username = request.POST.get('username')
        email = request.POST.get('email', '')
        user_role = request.POST.get('role', 'student')
        phone = request.POST.get('phone', '')

        if User.objects.filter(username=username).exists():
            messages.error(request, f"User '{username}' already exists!")
        else:
            new_user = User.objects.create_user(username=username, email=email, password='123456')
            profile, _ = UserProfile.objects.get_or_create(user=new_user)
            profile.role = user_role
            profile.phone = phone
            profile.is_first_login = True
            profile.save()
            messages.success(request, f"Registered '{username}' ({user_role.upper()}) with default password '123456'.")
            return redirect('manage_students')

    users = UserProfile.objects.all() if role in ['admin', 'teacher'] else UserProfile.objects.filter(user=request.user)
    return render(request, 'portal/students.html', {'users': users, 'role': role})

@login_required
def branding_settings(request):
    if request.user.userprofile.is_first_login:
        return redirect('first_time_password_change')

    branding, _ = SchoolBranding.objects.get_or_create(id=1)
    if request.method == 'POST' and get_user_role(request.user) == 'admin':
        branding.school_name = request.POST.get('school_name', branding.school_name)
        branding.primary_color = request.POST.get('primary_color', branding.primary_color)
        branding.secondary_color = request.POST.get('secondary_color', branding.secondary_color)
        branding.tagline = request.POST.get('tagline', branding.tagline)
        branding.phone_number = request.POST.get('phone_number', branding.phone_number)
        branding.email_address = request.POST.get('email_address', branding.email_address)
        branding.save()
        messages.success(request, 'School branding & contact details updated permanently!')
        return redirect('branding_settings')

    return render(request, 'portal/branding.html', {'branding': branding})