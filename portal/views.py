from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import UserProfile, SchoolBranding, PendingModification, StudentProfile, Grade, FeeRecord, AcademicTerm

def get_common_context(request):
    active_term = AcademicTerm.objects.filter(is_active=True).first()
    branding = SchoolBranding.objects.first()
    if not branding:
        branding = SchoolBranding.objects.create()
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
    return render(request, 'portal/login.html')

def logout_view(request):
    logout(request)
    return redirect('portal:login')

@login_required
def dashboard(request):
    context = get_common_context(request)
    context.update({
        'active_tab': 'dashboard',
        'total_students': StudentProfile.objects.count(),
        'grades': Grade.objects.select_related('student', 'term')[:10],
        'pending_approvals': PendingModification.objects.filter(is_approved=False),
    })
    return render(request, 'portal/dashboard.html', context)

@login_required
def register_user_view(request):
    # Only Admin can register students and teachers
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'ADMIN':
        messages.error(request, 'Access denied. Only Admins can register new users.')
        return redirect('portal:portal_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        role = request.POST.get('role')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        else:
            user = User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name)
            UserProfile.objects.create(user=user, role=role)
            messages.success(request, f'Successfully registered {role} account for {username}.')
            return redirect('portal:portal_dashboard')

    context = get_common_context(request)
    context['active_tab'] = 'register'
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
        branding.primary_color = request.POST.get('primary_color', branding.primary_color)
        branding.secondary_color = request.POST.get('secondary_color', branding.secondary_color)
        branding.save()
        messages.success(request, 'Branding updated successfully.')
        return redirect('portal:update_branding')

    context = get_common_context(request)
    context['active_tab'] = 'branding'
    return render(request, 'portal/branding.html', context)

@login_required
def submit_modification_view(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        PendingModification.objects.create(teacher=request.user, title=title, description=description)
        messages.success(request, 'Modification request submitted to Admin for approval.')
        return redirect('portal:academics_view')

@login_required
def approve_modification_view(request, mod_id):
    if hasattr(request.user, 'profile') and request.user.profile.role == 'ADMIN':
        mod = get_object_or_404(PendingModification, id=mod_id)
        mod.is_approved = True
        mod.save()
        messages.success(request, 'Modification request approved.')
    return redirect('portal:portal_dashboard')

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
    context['students'] = StudentProfile.objects.all()
    context['pending_mods'] = PendingModification.objects.filter(teacher=request.user)
    return render(request, 'portal/academics.html', context)

@login_required
def finance_view(request):
    context = get_common_context(request)
    context['active_tab'] = 'finance'
    context['fee_records'] = FeeRecord.objects.all()
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