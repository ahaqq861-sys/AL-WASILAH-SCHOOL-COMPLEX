from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    """
    Main dashboard router for Students, Teachers, and Admins.
    """
    user = request.user

    # Redirect superusers directly to Django Admin
    if user.is_superuser or user.is_staff:
        context = {'role': 'Admin'}
        return render(request, 'portal/dashboard.html', context)

    # Context for standard portal users (Teachers / Students)
    context = {
        'user': user,
        'role': getattr(user, 'role', 'User'),
    }
    return render(request, 'portal/dashboard.html', context)