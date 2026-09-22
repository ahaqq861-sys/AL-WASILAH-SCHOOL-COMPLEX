from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from .models import Student, FeeLedger, Grade, Announcement

class CustomLoginView(LoginView):
    template_name = 'portal/login.html'


@login_required
def dashboard(request):
    user = request.user
    context = {
        'announcements': Announcement.objects.all().order_by('-created_at')[:5]
    }

    if hasattr(user, 'student_profile'):
        student = user.student_profile
        context['student'] = student
        context['fees'] = FeeLedger.objects.filter(student=student)
        context['grades'] = Grade.objects.filter(student=student)
        return render(request, 'portal/student_dashboard.html', context)
        
    return render(request, 'portal/dashboard.html', context)