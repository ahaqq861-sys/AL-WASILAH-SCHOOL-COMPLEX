from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.shortcuts import redirect, render

from .models import SchoolBranding


def get_branding():
    """Safely retrieves or creates default school branding without throwing IntegrityError."""
    branding, _ = SchoolBranding.objects.get_or_create(
        id=1,
        defaults={
            "school_name": "Al-Wasilah School Complex",
            "tagline": "Knowledge and Virtue",
            "primary_color": "#800020",
        },
    )
    return branding


def custom_login(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("dashboard")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(
        request,
        "portal/login.html",
        {"form": form, "branding": get_branding()},
    )


@login_required
def dashboard(request):
    return render(
        request,
        "portal/dashboard.html",
        {"user": request.user, "branding": get_branding()},
    )


@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password was successfully updated!")
            return redirect("dashboard")
        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = PasswordChangeForm(request.user)

    return render(
        request,
        "portal/change_password.html",
        {"form": form, "branding": get_branding()},
    )


@login_required
def manage_students(request):
    return render(
        request,
        "portal/manage_students.html",
        {"branding": get_branding()},
    )


@login_required
def manage_teachers(request):
    return render(
        request,
        "portal/manage_teachers.html",
        {"branding": get_branding()},
    )


@login_required
def student_assessment(request):
    return render(
        request,
        "portal/student_assessment.html",
        {"branding": get_branding()},
    )


@login_required
def student_schedule(request):
    return render(
        request,
        "portal/student_schedule.html",
        {"branding": get_branding()},
    )


@login_required
def student_attendance(request):
    return render(
        request,
        "portal/student_attendance.html",
        {"branding": get_branding()},
    )


def custom_logout(request):
    logout(request)
    return redirect("login")