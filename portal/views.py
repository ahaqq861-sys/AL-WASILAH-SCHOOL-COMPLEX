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
        form = PasswordChangeForm(request.user)

    return render(request, 'portal/first_time_password.html', {'form': form})

@login_required
def portal_dashboard(request):
    if hasattr(request.user, 'userprofile') and request.user.userprofile.is_first_login:
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
def manage_profile(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        profile.first_name = request.POST.get('first_name', profile.first_name)
        profile.last_name = request.POST.get('last_name', profile.last_name)
        profile.sex = request.POST.get('sex', profile.sex)
        profile.phone = request.POST.get('phone', profile.phone)
        
        dob = request.POST.get('date_of_birth')
        if dob:
            profile.date_of_birth = dob
            
        if 'passport_photo' in request.FILES:
            profile.passport_photo = request.FILES['passport_photo']
            
        profile.save()
        messages.success(request, 'Profile details and passport picture updated successfully.')
        return redirect('manage_profile')
        
    return render(request, 'portal/profile.html', {'profile': profile})

@login_required
def manage_students(request):
    role = get_user_role(request.user)

    # Allow Admin or Teacher to register student accounts and upload their full profile data
    if request.method == 'POST' and role in ['admin', 'teacher']:
        user_id = request.POST.get('user_id')
        
        # Action A: Update an existing student's profile details & photo
        if user_id:
            profile = get_object_or_404(UserProfile, id=user_id)
            profile.first_name = request.POST.get('first_name', profile.first_name)
            profile.last_name = request.POST.get('last_name', profile.last_name)
            profile.sex = request.POST.get('sex', profile.sex)
            profile.phone = request.POST.get('phone', profile.phone)
            
            dob = request.POST.get('date_of_birth')
            if dob:
                profile.date_of_birth = dob
                
            if 'passport_photo' in request.FILES:
                profile.passport_photo = request.FILES['passport_photo']
                
            profile.save()
            messages.success(request, f"Profile updated for {profile.user.username}.")
            return redirect('manage_students')

        # Action B: Create a brand new user account
        else:
            username = request.POST.get('username')
            email = request.POST.get('email', '')
            user_role = request.POST.get('role', 'student')
            can_brand = True if request.POST.get('can_edit_branding') == 'on' and user_role == 'teacher' else False

            if User.objects.filter(username=username).exists():
                messages.error(request, f"User '{username}' already exists!")
            else:
                new_user = User.objects.create_user(username=username, email=email, password='123456')
                profile, _ = UserProfile.objects.get_or_create(user=new_user)
                profile.role = user_role
                profile.first_name = request.POST.get('first_name', '')
                profile.last_name = request.POST.get('last_name', '')
                profile.sex = request.POST.get('sex', '')
                profile.phone = request.POST.get('phone', '')
                profile.can_edit_branding = can_brand
                profile.is_first_login = True
                
                dob = request.POST.get('date_of_birth')
                if dob:
                    profile.date_of_birth = dob
                    
                if 'passport_photo' in request.FILES:
                    profile.passport_photo = request.FILES['passport_photo']
                    
                profile.save()
                messages.success(request, f"Registered '{username}' ({user_role.upper()}). Default password: 123456.")
                return redirect('manage_students')

    users = UserProfile.objects.all() if role in ['admin', 'teacher'] else UserProfile.objects.filter(user=request.user)
    return render(request, 'portal/students.html', {'users': users, 'role': role})

@login_required
def branding_settings(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    
    if profile.role == 'student' or (profile.role == 'teacher' and not profile.can_edit_branding):
        messages.error(request, 'Access Denied: You do not have authorization to edit school branding.')
        return redirect('portal_dashboard')

    branding, _ = SchoolBranding.objects.get_or_create(id=1)
    
    if request.method == 'POST':
        branding.school_name = request.POST.get('school_name', branding.school_name)
        branding.tagline = request.POST.get('tagline', branding.tagline)
        branding.primary_color = request.POST.get('primary_color', branding.primary_color)
        branding.secondary_color = request.POST.get('secondary_color', branding.secondary_color)
        branding.phone_number = request.POST.get('phone_number', branding.phone_number)
        branding.email_address = request.POST.get('email_address', branding.email_address)
        branding.address = request.POST.get('address', branding.address)
        
        if 'logo' in request.FILES:
            branding.logo = request.FILES['logo']
            
        branding.save()
        messages.success(request, 'School logo, contacts, and branding updated permanently!')
        return redirect('branding_settings')

    return render(request, 'portal/branding.html', {'branding': branding})

@login_required
def student_grades(request):
    role = get_user_role(request.user)
    
    if request.method == 'POST' and role in ['admin', 'teacher']:
        student_id = request.POST.get('student_id')
        subject = request.POST.get('subject')
        score = request.POST.get('score')
        term = request.POST.get('term', 'Term 1')
        
        student = get_object_or_404(User, id=student_id)
        StudentGrade.objects.create(student=student, subject=subject, score=score, term=term)
        messages.success(request, f"Grade successfully recorded for {student.username}.")
        return redirect('student_grades')

    # Students see only their own results; Admins/Teachers see all uploaded grades
    grades = StudentGrade.objects.filter(student=request.user) if role == 'student' else StudentGrade.objects.all()
    students = UserProfile.objects.filter(role='student')
    return render(request, 'portal/grades.html', {'grades': grades, 'role': role, 'students': students})

@login_required
def fee_statement(request):
    role = get_user_role(request.user)
    
    if request.method == 'POST' and role in ['admin', 'teacher']:
        student_id = request.POST.get('student_id')
        amount_paid = request.POST.get('amount_paid')
        total_fee = request.POST.get('total_fee')
        
        student = get_object_or_404(User, id=student_id)
        FeePayment.objects.create(student=student, amount_paid=amount_paid, total_fee=total_fee)
        messages.success(request, f"Fee payment recorded for {student.username}.")
        return redirect('fee_statement')

    # Students view only their individual payment receipts; Teachers/Admins see overall ledger
    payments = FeePayment.objects.filter(student=request.user) if role == 'student' else FeePayment.objects.all()
    students = UserProfile.objects.filter(role='student')
    return render(request, 'portal/fees.html', {'payments': payments, 'role': role, 'students': students})