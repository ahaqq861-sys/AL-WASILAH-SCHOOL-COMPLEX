from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def custom_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Check role permissions/flags
            if role == 'admin' and not (user.is_superuser or user.is_staff):
                messages.error(request, "Account does not have Administrative privileges.")
                return render(request, 'portal/login.html')

            login(request, user)
            # Save selected role into session to load the correct interface
            request.session['selected_role'] = role
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'portal/login.html')

def custom_logout(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    role = request.session.get('selected_role')

    # Fallback default role assignment based on user properties
    if not role:
        if request.user.is_superuser or request.user.is_staff:
            role = 'admin'
        elif getattr(request.user, 'is_teacher', False):
            role = 'teacher'
        else:
            role = 'student'

    context = {
        'user': request.user,
        'role': role,
    }

    if role == 'admin':
        return render(request, 'portal/admin_dashboard.html', context)
    elif role == 'teacher':
        return render(request, 'portal/teacher_dashboard.html', context)
    else:
        return render(request, 'portal/student_dashboard.html', context)