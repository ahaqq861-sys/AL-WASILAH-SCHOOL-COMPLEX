from django.shortcuts import render
from .models import StudentProfile, Grade, FeeRecord, AcademicTerm, ClassLevel

def get_common_context():
    active_term = AcademicTerm.objects.filter(is_active=True).first()
    return {
        'active_term': active_term,
        'school_name': 'Al-Wasilah School Complex',
    }

def dashboard(request):
    context = get_common_context()
    students = StudentProfile.objects.all()
    fee_records = FeeRecord.objects.all()
    
    total_students = students.count()
    total_due = sum(f.amount_due for f in fee_records)
    total_paid = sum(f.amount_paid for f in fee_records)
    balance = total_due - total_paid

    context.update({
        'active_tab': 'dashboard',
        'total_students': total_students,
        'total_due': total_due,
        'total_paid': total_paid,
        'balance': balance,
        'grades': Grade.objects.select_related('student', 'term')[:10],
    })
    return render(request, 'portal/dashboard.html', context)

def profile_view(request):
    context = get_common_context()
    context['active_tab'] = 'profile'
    return render(request, 'portal/placeholder.html', context)

def inbox_view(request):
    context = get_common_context()
    context['active_tab'] = 'inbox'
    return render(request, 'portal/placeholder.html', context)

def calendar_view(request):
    context = get_common_context()
    context['active_tab'] = 'calendar'
    return render(request, 'portal/placeholder.html', context)

def help_view(request):
    context = get_common_context()
    context['active_tab'] = 'help'
    return render(request, 'portal/placeholder.html', context)

def academics_view(request):
    context = get_common_context()
    context['active_tab'] = 'academics'
    context['students'] = StudentProfile.objects.select_related('current_class').all()
    return render(request, 'portal/academics.html', context)

def accommodation_view(request):
    context = get_common_context()
    context['active_tab'] = 'accommodation'
    return render(request, 'portal/placeholder.html', context)

def finance_view(request):
    context = get_common_context()
    context['active_tab'] = 'finance'
    context['fee_records'] = FeeRecord.objects.select_related('student', 'term').all()
    return render(request, 'portal/finance.html', context)

def health_view(request):
    context = get_common_context()
    context['active_tab'] = 'health'
    return render(request, 'portal/placeholder.html', context)

def counselling_view(request):
    context = get_common_context()
    context['active_tab'] = 'counselling'
    return render(request, 'portal/placeholder.html', context)