import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum
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
        messages.error(request, 'Invalid username or password.')
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
        'grades': Grade.objects.filter(student=request.user) if profile and profile.role == 'STUDENT' else Grade.objects.select_related('student', 'course', 'term')[:10],
    })
    return render(request, 'portal/dashboard.html', context)

@login_required
def register_user_view(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'ADMIN':
        messages.error(request, 'Only Admins can register new users.')
        return redirect('portal:portal_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        role = request.POST.get('role')
        class_id = request.POST.get('assigned_class')
        course_ids = request.POST.getlist('assigned_courses')
        child_ids = request.POST.getlist('assigned_children')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        else:
            user = User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name)
            profile = UserProfile.objects.create(user=user, role=role)
            
            if role == 'STUDENT' and class_id:
                profile.assigned_class = ClassLevel.objects.get(id=class_id)
            elif role == 'TEACHER':
                profile.assigned_courses.set(Course.objects.filter(id__in=course_ids))
            elif role == 'PARENT':
                profile.children.set(User.objects.filter(id__in=child_ids))
            profile.save()

            messages.success(request, f'Permanently registered {role}: {username}')
            return redirect('portal:register_user')

    context = get_common_context(request)
    context['active_tab'] = 'register'
    context['classes'] = ClassLevel.objects.all()
    context['courses'] = Course.objects.all()
    context['students'] = UserProfile.objects.filter(role='STUDENT')
    return render(request, 'portal/register_user.html', context)

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
    if not hasattr(request.user, 'profile') or request.user.profile.role not in ['ADMIN', 'TEACHER']:
        messages.error(request, 'Access denied.')
        return redirect('portal:portal_dashboard')

    if request.method == 'POST':
        date = request.POST.get('date')
        term_id = request.POST.get('term_id')
        
        for key, value in request.POST.items():
            if key.startswith('status_'):
                student_id = key.split('_')[1]
                Attendance.objects.update_or_create(
                    student_id=student_id,
                    date=date,
                    defaults={'status': value, 'term_id': term_id}
                )
        messages.success(request, 'Attendance permanently recorded.')
        return redirect('portal:attendance_view')

    context = get_common_context(request)
    context['active_tab'] = 'attendance'
    context['students'] = UserProfile.objects.filter(role='STUDENT').select_related('user', 'assigned_class')
    context['terms'] = AcademicTerm.objects.all()
    return render(request, 'portal/attendance.html', context)

@login_required
def upload_results_view(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role not in ['ADMIN', 'TEACHER']:
        messages.error(request, 'Access denied.')
        return redirect('portal:portal_dashboard')

    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        course_id = request.POST.get('course_id')
        term_id = request.POST.get('term_id')
        score = request.POST.get('score')
        letter = request.POST.get('grade_letter')
        remark = request.POST.get('teacher_remark', 'Good performance.')

        Grade.objects.update_or_create(
            student_id=student_id,
            course_id=course_id,
            term_id=term_id,
            defaults={'score': score, 'grade_letter': letter, 'teacher_remark': remark}
        )
        messages.success(request, 'Academic result permanently saved.')
        return redirect('portal:academics_view')

@login_required
def record_payment_view(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'ADMIN':
        messages.error(request, 'Access restricted to Admin.')
        return redirect('portal:portal_dashboard')

    if request.method == 'POST':
        fee_id = request.POST.get('fee_record_id')
        amount = float(request.POST.get('amount'))
        method = request.POST.get('payment_method', 'Cash')

        fee_record = get_object_or_404(FeeRecord, id=fee_id)
        fee_record.amount_paid = float(fee_record.amount_paid) + amount
        fee_record.save()

        receipt = f"REC-{uuid.uuid4().hex[:8].upper()}"
        PaymentTransaction.objects.create(
            fee_record=fee_record,
            amount=amount,
            receipt_number=receipt,
            payment_method=method
        )
        messages.success(request, f'Payment of GHS {amount} saved. Receipt: {receipt}')
        return redirect('portal:finance_view')

@login_required
def upload_fees_view(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'ADMIN':
        messages.error(request, 'Access restricted to Admin.')
        return redirect('portal:portal_dashboard')

    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        term_id = request.POST.get('term_id')
        amount_due = request.POST.get('amount_due')

        FeeRecord.objects.update_or_create(
            student_id=student_id,
            term_id=term_id,
            defaults={'amount_due': amount_due}
        )
        messages.success(request, 'Trimester fee permanently set.')
        return redirect('portal:finance_view')

@login_required
def create_announcement_view(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        class_id = request.POST.get('target_class')
        
        target = ClassLevel.objects.get(id=class_id) if class_id else None
        Announcement.objects.create(
            title=title,
            content=content,
            author=request.user,
            target_class=target
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

    if request.method == 'POST' and request.user.profile.role == 'ADMIN':
        class_id = request.POST.get('class_id')
        course_id = request.POST.get('course_id')
        day = request.POST.get('day')
        start = request.POST.get('start_time')
        end = request.POST.get('end_time')

        TimetableSchedule.objects.create(
            class_level_id=class_id,
            course_id=course_id,
            day=day,
            start_time=start,
            end_time=end
        )
        messages.success(request, 'Timetable schedule permanently added.')
        return redirect('portal:timetable_view')

    return render(request, 'portal/timetable.html', context)

@login_required
def update_branding_view(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'ADMIN':
        messages.error(request, 'Access restricted to Admin.')
        return redirect('portal:portal_dashboard')

    branding = SchoolBranding.objects.first() or SchoolBranding.objects.create()
    if request.method == 'POST':
        branding.school_name = request.POST.get('school_name', branding.school_name)
        branding.logo_text = request.POST.get('logo_text', branding.logo_text)
        branding.primary_color = request.POST.get('primary_color', branding.primary_color)
        branding.secondary_color = request.POST.get('secondary_color', branding.secondary_color)
        branding.save()
        messages.success(request, 'Branding updated.')
        return redirect('portal:update_branding')

    context = get_common_context(request)
    context['active_tab'] = 'branding'
    return render(request, 'portal/branding.html', context)

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
def health_view(request):
    context = get_common_context(request)
    context['active_tab'] = 'health'
    return render(request, 'portal/placeholder.html', context)

@login_required
def counselling_view(request):
    context = get_common_context(request)
    context['active_tab'] = 'counselling'
    return render(request, 'portal/placeholder.html', context)