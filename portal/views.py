from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum
from .models import StudentProfile, TeacherProfile, ClassLevel, AcademicTerm, Grade, FeeRecord

# Check user roles
def is_admin(user):
    return user.is_staff or user.is_superuser

def is_teacher(user):
    return hasattr(user, 'teacherprofile') or user.is_staff

# Login View
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        u_name = request.POST.get('username')
        p_word = request.POST.get('password')
        user = authenticate(request, username=u_name, password=p_word)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
            
    return render(request, 'portal/login.html')

# Logout View
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')

# Unified Dashboard View
@login_required
def dashboard(request):
    user = request.user
    current_term = AcademicTerm.objects.filter(is_current=True).first()
    
    context = {
        'current_term': current_term,
    }

    # Admin View Context
    if user.is_staff or user.is_superuser:
        context['total_students'] = StudentProfile.objects.filter(is_graduated=False).count()
        context['total_teachers'] = TeacherProfile.objects.count()
        context['total_classes'] = ClassLevel.objects.count()
        return render(request, 'portal/admin_dashboard.html', context)
        
    # Teacher View Context
    elif hasattr(user, 'teacherprofile'):
        teacher = user.teacherprofile
        assigned_classes = teacher.assigned_classes.all()
        students = StudentProfile.objects.filter(current_class__in=assigned_classes, is_graduated=False)
        context['assigned_classes'] = assigned_classes
        context['students'] = students
        return render(request, 'portal/teacher_dashboard.html', context)
        
    # Student View Context
    elif hasattr(user, 'studentprofile'):
        student = user.studentprofile
        grades = Grade.objects.filter(student=student)
        fee_records = FeeRecord.objects.filter(student=student)
        
        total_due = fee_records.aggregate(Sum('amount_due'))['amount_due__sum'] or 0
        total_paid = fee_records.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
        balance = total_due - total_paid

        context['student'] = student
        context['grades'] = grades
        context['fee_records'] = fee_records
        context['total_due'] = total_due
        context['total_paid'] = total_paid
        context['balance'] = balance
        return render(request, 'portal/student_dashboard.html', context)

    return render(request, 'portal/dashboard.html', context)

# Class-Based Gradebook Entry
@login_required
@user_passes_test(is_teacher)
def gradebook_view(request):
    current_term = AcademicTerm.objects.filter(is_current=True).first()
    selected_class_id = request.GET.get('class_id')
    
    classes = ClassLevel.objects.all()
    students = []
    
    if selected_class_id:
        selected_class = get_object_or_404(ClassLevel, id=selected_class_id)
        students = StudentProfile.objects.filter(current_class=selected_class, is_graduated=False)
    
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        subject_name = request.POST.get('subject_name')
        score = request.POST.get('score')
        
        if student_id and subject_name and score and current_term:
            student = get_object_or_404(StudentProfile, id=student_id)
            Grade.objects.create(
                student=student,
                term=current_term,
                subject_name=subject_name,
                score=score
            )
            messages.success(request, f'Grade recorded successfully for {student.user.get_full_name()}.')
            return redirect(f'{request.path}?class_id={selected_class_id}')

    context = {
        'classes': classes,
        'selected_class_id': selected_class_id,
        'students': students,
        'current_term': current_term,
    }
    return render(request, 'portal/gradebook.html', context)

# Fee Management Ledger
@login_required
@user_passes_test(is_admin)
def fee_ledger_view(request):
    current_term = AcademicTerm.objects.filter(is_current=True).first()
    selected_class_id = request.GET.get('class_id')
    
    classes = ClassLevel.objects.all()
    students = []
    
    if selected_class_id:
        selected_class = get_object_or_404(ClassLevel, id=selected_class_id)
        students = StudentProfile.objects.filter(current_class=selected_class, is_graduated=False)

    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        amount_due = request.POST.get('amount_due', 0)
        amount_paid = request.POST.get('amount_paid', 0)
        
        if student_id and current_term:
            student = get_object_or_404(StudentProfile, id=student_id)
            fee_record, created = FeeRecord.objects.get_or_create(
                student=student,
                term=current_term,
                defaults={'amount_due': amount_due, 'amount_paid': amount_paid}
            )
            if not created:
                fee_record.amount_due = amount_due
                fee_record.amount_paid = amount_paid
                fee_record.save()
                
            messages.success(request, f'Fee ledger updated for {student.user.get_full_name()}.')
            return redirect(f'{request.path}?class_id={selected_class_id}')

    context = {
        'classes': classes,
        'selected_class_id': selected_class_id,
        'students': students,
        'current_term': current_term,
    }
    return render(request, 'portal/fee_ledger.html', context)