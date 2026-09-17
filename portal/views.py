from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
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
        context['grades'] = StudentGrade.objects.all()
        context['payments'] = FeePayment.objects.all()
    elif role == 'teacher':
        context['grades'] = StudentGrade.objects.all()
    elif role == 'student':
        context['grades'] = StudentGrade.objects.filter(student=request.user)
        context['payments'] = FeePayment.objects.filter(student=request.user)

    return render(request, 'portal/dashboard.html', context)

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