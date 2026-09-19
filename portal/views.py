from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import UserProfile, SchoolBranding, AcademicTerm, Grade, FeeRecord, ClassLevel, Course

def get_common_context(request):
    active_term = AcademicTerm.objects.filter(is_active=True).first()
    branding = SchoolBranding.objects.first() or SchoolBranding.objects.create()
    return {
        'active_term': active_term,
        'branding': branding,
        'user_profile': getattr(request.user, 'profile', None) if request.user.is_authenticated else None,
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
    context.update({
        'active_tab': 'dashboard',
        'total_students': UserProfile.objects.filter(role='STUDENT').count(),
        'grades': Grade.objects.select_related('student', 'course', 'term')[:10],
    })
    return render(request, 'portal/dashboard.html', context)

@login_required
def register_user_view(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'ADMIN':
        messages.error(request, 'Only Admins can register students and teachers.')
        return redirect('portal:portal_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        role = request.POST.get('role')
        class_id = request.POST.get('assigned_class')
        course_ids = request.POST.getlist('assigned_courses')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        else:
            user = User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name)
            profile = UserProfile.objects.create(user=user, role=role)
            
            if role == 'STUDENT' and class_id:
                profile.assigned_class = ClassLevel.objects.get(id=class_id)
            elif role == 'TEACHER':
                profile.assigned_courses.set(Course.objects.filter(id__in=course_ids))
            profile.save()

            messages.success(request, f'Successfully registered {role}: {username}')
            return redirect('portal:register_user')

    context = get_common_context(request)
    context['active_tab'] = 'register'
    context['classes'] = ClassLevel.objects.all()
    context['courses'] = Course.objects.all()
    return render(request, 'portal/register_user.html', context)

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

        Grade.objects.create(
            student_id=student_id,
            course_id=course_id,
            term_id=term_id,
            score=score,
            grade_letter=letter
        )
        messages.success(request, 'Academic result uploaded successfully.')
        return redirect('portal:academics_view')

@login_required
def upload_fees_view(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'ADMIN':
        messages.error(request, 'Access restricted to Admin.')
        return redirect('portal:portal_dashboard')

    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        term_id = request.POST.get('term_id')
        amount_due = request.POST.get('amount_due')
        amount_paid = request.POST.get('amount_paid')

        FeeRecord.objects.create(
            student_id=student_id,
            term_id=term_id,
            amount_due=amount_due,
            amount_paid=amount_paid
        )
        messages.success(request, 'Trimester fee record uploaded.')
        return redirect('portal:finance_view')

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
    context['fee_records'] = FeeRecord.objects.select_related('student', 'term').all()
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