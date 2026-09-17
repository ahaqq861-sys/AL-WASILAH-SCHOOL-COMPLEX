from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile, StudentGrade, FeePayment, SchoolBranding

def custom_login(request):
    if request.user.is_authenticated:
        return redirect('portal_dashboard')

    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            return redirect('portal_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'portal/login.html')

def custom_logout(request):
    logout(request)
    return redirect('portal_login')

@login_required
def portal_dashboard(request):
    try:
        profile = request.user.userprofile
        role = profile.role
    except UserProfile.DoesNotExist:
        role = 'student'

    context = {'role': role}

    if role == 'admin':
        context['profiles'] = UserProfile.objects.all()
        context['grades'] = StudentGrade.objects.all().order_by('-date_recorded')[:10]
        context['payments'] = FeePayment.objects.all().order_by('-date_paid')[:10]
    elif role == 'teacher':
        context['grades'] = StudentGrade.objects.all().order_by('-date_recorded')
    elif role == 'student':
        context['grades'] = StudentGrade.objects.filter(student=request.user)
        context['payments'] = FeePayment.objects.filter(student=request.user)

    return render(request, 'portal/dashboard.html', context)

@login_required
def student_grades(request):
    if request.user.userprofile.role == 'student':
        grades = StudentGrade.objects.filter(student=request.user)
    else:
        grades = StudentGrade.objects.all()
    return render(request, 'portal/grades.html', {'grades': grades})

@login_required
def fee_statement(request):
    if request.user.userprofile.role == 'student':
        payments = FeePayment.objects.filter(student=request.user)
    else:
        payments = FeePayment.objects.all()
    return render(request, 'portal/fees.html', {'payments': payments})

@login_required
def print_student_report(request, student_id=None):
    if student_id and request.user.userprofile.role in ['admin', 'teacher']:
        target_student = get_object_or_404(User, id=student_id)
    else:
        target_student = request.user

    grades = StudentGrade.objects.filter(student=target_student)
    payments = FeePayment.objects.filter(student=target_student)
    
    return render(request, 'portal/print_report.html', {
        'target_student': target_student,
        'grades': grades,
        'payments': payments
    })

@login_required
def print_fee_receipt(request, payment_id):
    payment = get_object_or_404(FeePayment, id=payment_id)
    if request.user.userprofile.role == 'student' and payment.student != request.user:
        messages.error(request, 'Unauthorized access to receipt.')
        return redirect('fee_statement')
        
    return render(request, 'portal/print_receipt.html', {'payment': payment})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('portal_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'portal/change_password.html', {'form': form})