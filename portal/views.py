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

    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            profile, _ = UserProfile.objects.get_or_create(user=user)
            if profile.is_first_login:
                messages.warning(request, 'First-time login detected. Please set your permanent password.')
                return redirect('first_time_password_change')
            return redirect('portal_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'portal/login.html')

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
            messages.success(request, 'Password changed successfully! Welcome to your dashboard.')
            return redirect('portal_dashboard')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'portal/first_time_password.html', {'form': form})

@login_required
def portal_dashboard(request):
    if hasattr(request.user, 'userprofile') and request.user.userprofile.is_first_login:
        return redirect('first_time_password_change')

    role = get_user_role(request.user)
    context = {'role': role}
    if role == 'admin':
        context['profiles'] = UserProfile.objects.all()
        context['grades'] = StudentGrade.objects.all().order_by('-date_recorded')[:10]
        context['payments'] = FeePayment.objects.all().order_by('-date_paid')[:10]
        context['total_students'] = UserProfile.objects.filter(role='student').count()
        context['total_teachers'] = UserProfile.objects.filter(role='teacher').count()
    elif role == 'teacher':
        context['grades'] = StudentGrade.objects.all().order_by('-date_recorded')
    elif role == 'student':
        context['grades'] = StudentGrade.objects.filter(student=request.user)
        context['payments'] = FeePayment.objects.filter(student=request.user)

    return render(request, 'portal/dashboard.html', context)

@login_required
def manage_students(request):
    if hasattr(request.user, 'userprofile') and request.user.userprofile.is_first_login:
        return redirect('first_time_password_change')

    role = get_user_role(request.user)
    
    # Handle New User Creation by Admin (Default Password = 123456)
    if request.method == 'POST' and role == 'admin':
        username = request.POST.get('username')
        email = request.POST.get('email', '')
        user_role = request.POST.get('role', 'student')
        phone = request.POST.get('phone', '')

        if User.objects.filter(username=username).exists():
            messages.error(request, f"User '{username}' already exists!")
        else:
            new_user = User.objects.create_user(username=username, email=email, password='123456')
            profile, created = UserProfile.objects.get_or_create(user=new_user)
            profile.role = user_role
            profile.phone = phone
            profile.is_first_login = True
            profile.save()
            messages.success(request, f"Account created for '{username}' ({user_role.upper()}) with default password '123456'.")
            return redirect('manage_students')

    users = UserProfile.objects.all() if role in ['admin', 'teacher'] else UserProfile.objects.filter(user=request.user)
    return render(request, 'portal/students.html', {'users': users, 'role': role})

@login_required
def student_grades(request):
    if hasattr(request.user, 'userprofile') and request.user.userprofile.is_first_login:
        return redirect('first_time_password_change')

    role = get_user_role(request.user)
    
    # Add new grade (Teachers and Admins)
    if request.method == 'POST' and role in ['admin', 'teacher']:
        student_id = request.POST.get('student_id')
        subject = request.POST.get('subject')
        score = request.POST.get('score')
        term = request.POST.get('term', 'Term 1')
        student = get_object_or_404(User, id=student_id)
        StudentGrade.objects.create(student=student, subject=subject, score=score, term=term)
        messages.success(request, f"Grade recorded for {student.username}.")
        return redirect('student_grades')

    grades = StudentGrade.objects.filter(student=request.user) if role == 'student' else StudentGrade.objects.all()
    students = UserProfile.objects.filter(role='student')
    return render(request, 'portal/grades.html', {'grades': grades, 'role': role, 'students': students})

@login_required
def fee_statement(request):
    if hasattr(request.user, 'userprofile') and request.user.userprofile.is_first_login:
        return redirect('first_time_password_change')

    role = get_user_role(request.user)

    # Record payment (Admin only)
    if request.method == 'POST' and role == 'admin':
        student_id = request.POST.get('student_id')
        amount_paid = request.POST.get('amount_paid')
        total_fee = request.POST.get('total_fee')
        student = get_object_or_404(User, id=student_id)
        FeePayment.objects.create(student=student, amount_paid=amount_paid, total_fee=total_fee)
        messages.success(request, f"Fee payment of GH₵ {amount_paid} recorded for {student.username}.")
        return redirect('fee_statement')

    payments = FeePayment.objects.filter(student=request.user) if role == 'student' else FeePayment.objects.all()
    students = UserProfile.objects.filter(role='student')
    return render(request, 'portal/fees.html', {'payments': payments, 'role': role, 'students': students})

@login_required
def branding_settings(request):
    if hasattr(request.user, 'userprofile') and request.user.userprofile.is_first_login:
        return redirect('first_time_password_change')

    branding, _ = SchoolBranding.objects.get_or_create(id=1)
    if request.method == 'POST' and get_user_role(request.user) == 'admin':
        branding.school_name = request.POST.get('school_name', branding.school_name)
        branding.primary_color = request.POST.get('primary_color', branding.primary_color)
        branding.secondary_color = request.POST.get('secondary_color', branding.secondary_color)
        branding.tagline = request.POST.get('tagline', branding.tagline)
        branding.save()
        messages.success(request, 'Branding updated successfully!')
        return redirect('branding_settings')

    return render(request, 'portal/branding.html', {'branding': branding})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password updated successfully!')
            return redirect('portal_dashboard')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'portal/change_password.html', {'form': form})