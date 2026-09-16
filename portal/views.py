import secrets
import string
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import StudentProfile, TeacherProfile, SchoolBranding


def generate_temp_password(length=10):
    """Generates a secure temporary password."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def custom_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    try:
        branding = SchoolBranding.get_config()
    except Exception:
        branding = None
    
    if request.method == 'POST':
        # Clean username input manually to enforce lowercase and strip spaces
        post_data = request.POST.copy()
        if 'username' in post_data:
            post_data['username'] = post_data['username'].strip().lower()

        form = AuthenticationForm(request, data=post_data)
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
    """Logs out the current user and redirects to the login page."""
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    try:
        branding = SchoolBranding.get_config()
    except Exception:
        branding = None
    return render(request, 'portal/dashboard.html', {'branding': branding})


@login_required
def manage_students(request):
    try:
        branding = SchoolBranding.get_config()
    except Exception:
        branding = None

    generated_credentials = None

    if request.method == 'POST' and 'create_student' in request.POST:
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        student_id = request.POST.get('student_id', '').strip()
        current_class = request.POST.get('current_class', '').strip()
        guardian_contact = request.POST.get('guardian_contact', '').strip()

        username = student_id.lower()
        if User.objects.filter(username=username).exists():
            messages.error(request, f"A student account with ID/Username '{username}' already exists.")
        else:
            temp_password = generate_temp_password()
            new_user = User.objects.create_user(
                username=username,
                password=temp_password,
                first_name=first_name,
                last_name=last_name,
                is_active=True
            )
            StudentProfile.objects.create(
                user=new_user,
                student_id=student_id,
                current_class=current_class,
                guardian_contact=guardian_contact
            )
            generated_credentials = {
                'role': 'Student',
                'name': f"{first_name} {last_name}",
                'username': username,
                'password': temp_password,
            }
            messages.success(request, f"Student account created for {first_name} {last_name}!")

    try:
        students = StudentProfile.objects.select_related('user').all().order_by('current_class', 'user__first_name')
    except Exception:
        students = []

    context = {
        'branding': branding,
        'students': students,
        'generated_credentials': generated_credentials,
    }
    return render(request, 'portal/manage_students.html', context)


@login_required
def manage_teachers(request):
    try:
        branding = SchoolBranding.get_config()
    except Exception:
        branding = None

    generated_credentials = None

    if request.method == 'POST' and 'create_teacher' in request.POST:
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        employee_id = request.POST.get('employee_id', '').strip()
        subject_assigned = request.POST.get('subject_assigned', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()

        username = employee_id.lower()
        if User.objects.filter(username=username).exists():
            messages.error(request, f"A teacher account with Staff ID/Username '{username}' already exists.")
        else:
            temp_password = generate_temp_password()
            new_user = User.objects.create_user(
                username=username,
                password=temp_password,
                first_name=first_name,
                last_name=last_name,
                is_active=True
            )
            TeacherProfile.objects.create(
                user=new_user,
                employee_id=employee_id,
                subject_assigned=subject_assigned,
                phone_number=phone_number
            )
            generated_credentials = {
                'role': 'Teacher',
                'name': f"{first_name} {last_name}",
                'username': username,
                'password': temp_password,
            }
            messages.success(request, f"Teacher account created for {first_name} {last_name}!")

    try:
        teachers = TeacherProfile.objects.select_related('user').all().order_by('user__first_name')
    except Exception:
        teachers = []

    context = {
        'branding': branding,
        'teachers': teachers,
        'generated_credentials': generated_credentials,
    }
    return render(request, 'portal/manage_teachers.html', context)