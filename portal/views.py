from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile, FeeLedger, SubjectCourse, TimetableEntry, AcademicEvent, AcademicClass, SchoolBranding

@login_required
def dashboard(request):
    profile = getattr(request.user, 'profile', None)
    branding = SchoolBranding.objects.first()
    
    context = {
        'user_profile': profile,
        'branding': branding,
    }

    if profile and profile.role == 'STUDENT':
        user_class = profile.assigned_class
        current_term = branding.current_term if branding else "Trimester 1"
        
        context['courses'] = SubjectCourse.objects.filter(academic_class=user_class, term=current_term) if user_class else []
        context['timetable'] = TimetableEntry.objects.filter(academic_class=user_class) if user_class else []
        context['events'] = AcademicEvent.objects.order_by('event_date')
        context['fee_ledger'] = FeeLedger.objects.filter(student=profile, term=current_term).first()

    return render(request, 'portal/dashboard.html', context)

@login_required
def register_user(request):
    current_profile = getattr(request.user, 'profile', None)
    if not current_profile or current_profile.role not in ['ADMIN', 'TEACHER']:
        messages.error(request, "Access denied.")
        return redirect('/portal/')

    classes = AcademicClass.objects.all()
    
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        role = request.POST.get('role', 'STUDENT')
        class_id = request.POST.get('academic_class')
        index_number = request.POST.get('index_number')

        # Teachers can only register students into their own assigned class
        if current_profile.role == 'TEACHER':
            role = 'STUDENT'
            class_obj = current_profile.assigned_class
        else:
            class_obj = AcademicClass.objects.filter(id=class_id).first() if class_id else None

        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password
        )
        
        UserProfile.objects.create(
            user=user,
            role=role,
            assigned_class=class_obj,
            index_number=index_number
        )
        
        messages.success(request, f"User '{username}' registered successfully.")
        return redirect('/portal/')

    return render(request, 'portal/register_user.html', {'classes': classes, 'current_profile': current_profile})

@login_required
def edit_fee_ledger(request, ledger_id=None):
    current_profile = getattr(request.user, 'profile', None)
    
    if not current_profile or current_profile.role not in ['ADMIN', 'TEACHER']:
        messages.error(request, "Permission denied.")
        return redirect('/portal/')

    ledger = get_object_or_404(FeeLedger, id=ledger_id) if ledger_id else None

    # Teachers can only view/edit fee ledgers for students in their assigned class
    if current_profile.role == 'TEACHER' and ledger:
        if ledger.student.assigned_class != current_profile.assigned_class:
            messages.error(request, "You can only edit fee ledgers for your assigned class.")
            return redirect('/portal/')

    if request.method == 'POST':
        total_fees = request.POST.get('total_fees')
        amount_paid = request.POST.get('amount_paid')

        if ledger:
            ledger.total_fees = total_fees
            ledger.amount_paid = amount_paid
            ledger.save()
            messages.success(request, "Fee ledger updated successfully.")
        return redirect('/portal/')

    return render(request, 'portal/edit_fee_ledger.html', {'ledger': ledger})