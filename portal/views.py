from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SchoolBranding, StudentGrade, FeePayment, UserProfile, User
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

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
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'portal/change_password.html', {'form': form})

def custom_login(request):
    if request.user.is_authenticated:
        return redirect('portal_dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('portal_dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'portal/login.html', {'form': form})

@login_required
def portal_dashboard(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    role = profile.role

    context = {
        'role': role,
        'all_users': User.objects.all() if role == 'admin' else None,
        'grades': StudentGrade.objects.filter(student=request.user) if role == 'student' else StudentGrade.objects.all(),
        'fees': FeePayment.objects.filter(student=request.user) if role == 'student' else FeePayment.objects.all(),
    }
    return render(request, 'portal/dashboard.html', context)

def custom_logout(request):
    logout(request)
    return redirect('portal_login')