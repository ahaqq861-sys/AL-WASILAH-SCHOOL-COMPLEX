from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SchoolBranding, TeacherProfile, StudentProfile, GradeRecord, ClassSchedule, AttendanceRecord

def custom_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    branding = SchoolBranding.get_config()

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role', 'student')

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

    try:
        total_students = StudentProfile.objects.count()
    except Exception:
        total_students = 0

    try:
        total_teachers = TeacherProfile.objects.count()
    except Exception:
        total_teachers = 0

    students_list = StudentProfile.objects.select_related('user').all()
    teachers_list = TeacherProfile.objects.select_related('user').all()

    context = {
        'user': request.user,
        'role': role,
        'branding': branding,
        'total_students': total_students,
        'total_teachers': total_teachers,
        'students_list': students_list,
        'teachers_list': teachers_list,
    }

    if role == 'admin':
        return render(request, 'portal/admin_dashboard.html', context)
    elif role == 'teacher':
        return render(request, 'portal/teacher_dashboard.html', context)
    else:
        return render(request, 'portal/student_dashboard.html', context)


# ================= STUDENT VIEWS =================
@login_required
def student_assessment(request):
    branding = SchoolBranding.get_config()
    student_profile = getattr(request.user, 'student_profile', None)
    grades = GradeRecord.objects.filter(student=student_profile) if student_profile else []
    return render(request, 'portal/student_assessment.html', {'branding': branding, 'grades': grades})

@login_required
def student_schedule(request):
    branding = SchoolBranding.get_config()
    student_profile = getattr(request.user, 'student_profile', None)
    schedules = ClassSchedule.objects.filter(class_name=student_profile.current_class) if student_profile else []
    return render(request, 'portal/student_schedule.html', {'branding': branding, 'schedules': schedules})

@login_required
def student_attendance(request):
    branding = SchoolBranding.get_config()
    student_profile = getattr(request.user, 'student_profile', None)
    attendance = AttendanceRecord.objects.filter(student=student_profile) if student_profile else []
    return render(request, 'portal/student_attendance.html', {'branding': branding, 'attendance': attendance})


# ================= TEACHER VIEWS =================
@login_required
def teacher_roster(request):
    branding = SchoolBranding.get_config()
    teacher_profile = getattr(request.user, 'teacher_profile', None)
    students = StudentProfile.objects.filter(current_class=teacher_profile.assigned_class) if teacher_profile and teacher_profile.assigned_class else StudentProfile.objects.all()
    return render(request, 'portal/teacher_roster.html', {'branding': branding, 'students': students})

@login_required
def teacher_grade_entry(request):
    branding = SchoolBranding.get_config()
    students = StudentProfile.objects.all()

    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        subject = request.POST.get('subject')
        class_score = float(request.POST.get('class_score', 0))
        exam_score = float(request.POST.get('exam_score', 0))
        remarks = request.POST.get('remarks', '')

        student = get_object_or_404(StudentProfile, id=student_id)
        GradeRecord.objects.create(
            student=student,
            subject=subject,
            class_score=class_score,
            exam_score=exam_score,
            teacher_remarks=remarks
        )
        messages.success(request, f"Grade recorded successfully for {student.user.get_full_name() or student.user.username}!")
        return redirect('teacher_grade_entry')

    return render(request, 'portal/teacher_grade_entry.html', {'branding': branding, 'students': students})


# ================= ADMIN VIEWS =================
@login_required
def admin_students_db(request):
    branding = SchoolBranding.get_config()
    students = StudentProfile.objects.select_related('user').all()
    return render(request, 'portal/admin_students.html', {'branding': branding, 'students': students})

@login_required
def admin_teachers_db(request):
    branding = SchoolBranding.get_config()
    teachers = TeacherProfile.objects.select_related('user').all()
    return render(request, 'portal/admin_teachers.html', {'branding': branding, 'teachers': teachers})

@login_required
def create_user_account(request):
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