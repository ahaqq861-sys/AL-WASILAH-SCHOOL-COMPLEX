from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SchoolBranding, StudentGrade, FeePayment, UserProfile, User

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