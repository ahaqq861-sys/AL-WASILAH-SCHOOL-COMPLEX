import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import (
    UserProfile, SchoolBranding, AcademicTerm, Grade, FeeRecord, 
    PaymentTransaction, ClassLevel, Course, Attendance, TimetableSchedule, Announcement
)

def get_common_context(request):
    active_term = AcademicTerm.objects.filter(is_active=True).first()
    branding = SchoolBranding.objects.first() or SchoolBranding.objects.create()
    return {
        'active_term': active_term,
        'branding': branding,
        'user_profile': getattr(request.user, 'profile', None) if request.user.is_authenticated else None,
        'announcements': Announcement.objects.all().order_by('-created_at')[:5],
    }

def login_view(request):
    if request.user.is_authenticated:
        return redirect('portal:portal_dashboard')
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user:
            login(request, user)
            return redirect('portal:portal_dashboard')
        messages.error(request, 'Invalid Username / Index Number or Password.')
    return render(request, 'portal/login.html', get_common_context(request))

def logout_view(request):
    logout(request)
    return redirect('portal:login')

@login_required
def dashboard(request):
    context = get_common_context(request)
    profile = context['user_profile']
    if profile and profile.role == 'PARENT':
        context['children'] = profile.children.all()
    
    context.update({
        'active_tab': 'dashboard',
        'total_students': UserProfile.objects.filter(role='STUDENT').count(),
        'total_teachers': UserProfile.objects.filter(role='TEACHER').count(),
        'grades': Grade.objects.filter(student=request.user) if profile and profile.role == 'STUDENT' else Grade.objects.select_related('student', 'course', 'term')[:10],
    })
    return render(request, 'portal/dashboard.html', context)

@login_required
def register_user_view(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'ADMIN':
        messages.error(request, 'Only Admins can register new users.')
        return redirect('portal:portal_dashboard')

    # Ensure default classes exist so the dropdown is never empty
    if not ClassLevel.objects.exists():
        for default_cls in ['Basic 1', 'Basic 2', 'Basic 3', 'JHS 1', 'JHS 2', 'JHS 3']:
            ClassLevel.objects.get_or_create(name=default_cls)

    if request.method == 'POST':
        role = request.POST.get('role')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        dob = request.POST.get('date_of_birth')
        sex = request.POST.get('sex')
        gender = request.POST.get('gender')
        phone = request.POST.get('phone_number')
        study_status = request.POST.get('study_status', 'ACTIVE')
        class_id = request.POST.get('assigned_class')
        course_ids = request.POST.getlist('assigned_courses')
        passport = request.FILES.get('passport_picture')

        generated_username = request.POST.get('username') or f"{first_name.lower().strip()}{uuid.uuid4().hex[:4]}"
        generated_password = request.POST.get('password') or f"Pass@{uuid.uuid4().hex[:6]}"

        if User.objects.filter(username=generated_username).exists():
            messages.error(request, 'Username / Index Number already exists.')
        else:
            # 1. Create User (Signal automatically creates UserProfile)
            user = User.objects.create_user(
                username=generated_username, 
                password=generated_password, 
                first_name=first_name, 
                last_name=last_name
            )
            
            # 2. Safely update the auto-created profile instead of using .create()
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.role = role
            profile.date_of_birth = dob if dob else None
            profile.sex = sex
            profile.gender = gender
            profile.phone_number = phone
            profile.study_status = study_status
            if passport:
                profile.passport_picture = passport
            profile.guardian_name = request.POST.get('guardian_name', '')
            profile.guardian_phone = request.POST.get('guardian_phone', '')
            profile.guardian_email = request.POST.get('guardian_email', '')
            profile.guardian_relationship = request.POST.get('guardian_relationship', '')

            if role == 'STUDENT' and class_id:
                profile.assigned_class = ClassLevel.objects.filter(id=class_id).first()
            elif role == 'TEACHER':
                profile.assigned_courses.set(Course.objects.filter(id__in=course_ids))
            
            profile.save()

            messages.success(
                request, 
                f'Successfully Registered {role}: {first_name} {last_name} | Username: {generated_username} | Password: {generated_password} | Index: {profile.index_number}'
            )
            return redirect('portal:register_user')

    context = get_common_context(request)
    context['active_tab'] = 'register'
    context['classes'] = ClassLevel.objects.all()
    context['courses'] = Course.objects.all()
    context['students'] = UserProfile.objects.filter(role='STUDENT').select_related('user', 'assigned_class')
    context['teachers'] = UserProfile.objects.filter(role='TEACHER').select_related('user')
    return render(request, 'portal/register_user.html', context)

@login_required
def update_branding_view(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'ADMIN':
        messages.error(request, 'Access restricted to Admin.')
        return redirect('portal:portal_dashboard')

    branding = SchoolBranding.objects.first() or SchoolBranding.objects.create()
    if request.method == 'POST':
        branding.school_name = request.POST.get('school_name', branding.school_name)
        branding.logo_text = request.POST.get('logo_text', branding.logo_text)
        branding.contact_email = request.POST.get('contact_email', branding.contact_email)
        branding.contact_phone = request.POST.get('contact_phone', branding.contact_phone)
        branding.address = request.POST.get('address', branding.address)
        branding.primary_color = request.POST.get('primary_color', branding.primary_color)
        branding.secondary_color = request.POST.get('secondary_color', branding.secondary_color)
        
        if request.FILES.get('logo_image'):
            branding.logo_image = request.FILES.get('logo_image')
            
        branding.save()
        messages.success(request, 'School branding & contact details updated permanently.')
        return redirect('portal:update_branding')

    context = get_common_context(request)
    context['active_tab'] = 'branding'
    return render(request, 'portal/branding.html', context)

@login_required
def report_card_view(request, student_id, term_id):
    student = get_object_or_404(User, id=student_id)
    term = get_object_or_404(AcademicTerm, id=term_id)
    grades = Grade.objects.filter(student=student, term=term).select_related('course')
    attendance_count = Attendance.objects.filter(student=student, term=term, status='PRESENT').count()
    total_days = Attendance.objects.filter(student=student, term=term).count()

    context = get_common_context(request)
    context.update({
        'student_user': student,
        'term': term,
        'grades': grades,
        'attendance_count': attendance_count,
        'total_days': total_days,
    })
    return render(request, 'portal/report_card.html', context)

@login_required
def attendance_view(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        term_id = request.POST.get('term_id')
        for key, value in request.POST.items():
            if key.startswith('status_'):
                student_id = key.split('_')[1]
                Attendance.objects.update_or_create(
                    student_id=student_id, date=date, defaults={'status': value, 'term_id': term_id}
                )
        messages.success(request, 'Attendance recorded.')
        return redirect('portal:attendance_view')

    context = get_common_context(request)
    context['active_tab'] = 'attendance'
    context['students'] = UserProfile.objects.filter(role='STUDENT').select_related('user', 'assigned_class')
    context['terms'] = AcademicTerm.objects.all()
    return render(request, 'portal/attendance.html', context)

@login_required
def upload_results_view(request):
    if request.method == 'POST':
        Grade.objects.update_or_create(
            student_id=request.POST.get('student_id'),
            course_id=request.POST.get('course_id'),
            term_id=request.POST.get('term_id'),
            defaults={
                'score': request.POST.get('score'),
                'grade_letter': request.POST.get('grade_letter'),
                'teacher_remark': request.POST.get('teacher_remark', 'Good performance.')
            }
        )
        messages.success(request, 'Grade recorded.')
        return redirect('portal:academics_view')

@login_required
def record_payment_view(request):
    if request.method == 'POST':
        fee = get_object_or_404(FeeRecord, id=request.POST.get('fee_record_id'))
        amount = float(request.POST.get('amount'))
        fee.amount_paid = float(fee.amount_paid) + amount
        fee.save()
        receipt = f"REC-{uuid.uuid4().hex[:8].upper()}"
        PaymentTransaction.objects.create(fee_record=fee, amount=amount, receipt_number=receipt, payment_method=request.POST.get('payment_method', 'Cash'))
        messages.success(request, f'Payment of GHS {amount} saved. Receipt #{receipt}')
        return redirect('portal:finance_view')

@login_required
def upload_fees_view(request):
    if request.method == 'POST':
        FeeRecord.objects.update_or_create(
            student_id=request.POST.get('student_id'),
            term_id=request.POST.get('term_id'),
            defaults={'amount_due': request.POST.get('amount_due')}
        )
        messages.success(request, 'Fee record updated.')
        return redirect('portal:finance_view')

@login_required
def create_announcement_view(request):
    if request.method == 'POST':
        Announcement.objects.create(
            title=request.POST.get('title'),
            content=request.POST.get('content'),
            author=request.user,
            target_class_id=request.POST.get('target_class') or None
        )
        messages.success(request, 'Announcement posted.')
        return redirect('portal:portal_dashboard')

@login_required
def timetable_view(request):
    context = get_common_context(request)
    context['active_tab'] = 'timetable'
    context['schedules'] = TimetableSchedule.objects.select_related('class_level', 'course').all()
    context['classes'] = ClassLevel.objects.all()
    context['courses'] = Course.objects.all()
    return render(request, 'portal/timetable.html', context)

@login_required
def academics_view(request):
    context = get_common_context(request)
    context['active_tab'] = 'academics'
    context['students'] = UserProfile.objects.filter(role='STUDENT').select_related('user', 'assigned_class')
    context['courses'] = Course.objects.all()
    context['terms'] = AcademicTerm.objects.all()
    context['grades'] = Grade.objects.select_related('student', 'course', 'term').all()
    return render(request, 'portal/academics.html', context)

@login_required
def finance_view(request):
    context = get_common_context(request)
    context['active_tab'] = 'finance'
    context['students'] = UserProfile.objects.filter(role='STUDENT').select_related('user')
    context['terms'] = AcademicTerm.objects.all()
    context['fee_records'] = FeeRecord.objects.select_related('student', 'term').prefetch_related('transactions').all()
    return render(request, 'portal/finance.html', context)

@login_required
def profile_view(request):
    context = get_common_context(request)
    context['active_tab'] = 'profile'
    return render(request, 'portal/placeholder.html', context)

@login_required
def inbox_view(request):
    context = get_common_context(request)
    context['active_tab'] = 'inbox'
    return render(request, 'portal/placeholder.html', context)

@login_required
def calendar_view(request):
    context = get_common_context(request)
    context['active_tab'] = 'calendar'
    return render(request, 'portal/placeholder.html', context)

@login_required
def help_view(request):
    context = get_common_context(request)
    context['active_tab'] = 'help'
    return render(request, 'portal/placeholder.html', context)

@login_required
def health_view(request):
    context = get_common_context(request)
    context['active_tab'] = 'health'
    return render(request, 'portal/placeholder.html', context)

@login_required
def counselling_view(request):
    context = get_common_context(request)
    context['active_tab'] = 'counselling'
    return render(request, 'portal/placeholder.html', context)