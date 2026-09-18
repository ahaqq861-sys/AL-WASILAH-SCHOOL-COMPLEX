from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Student, Grade

def dashboard(request):
    total_students = Student.objects.count()
    total_due = sum(s.fees_due for s in Student.objects.all())
    total_paid = sum(s.fees_paid for s in Student.objects.all())
    balance = total_due - total_paid

    context = {
        'total_students': total_students,
        'total_due': total_due,
        'total_paid': total_paid,
        'balance': balance,
        'active_tab': 'dashboard'
    }
    return render(request, 'portal/dashboard.html', context)


def student_directory(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        name = request.POST.get('name')
        student_class = request.POST.get('class')
        gender = request.POST.get('gender')
        fees_due = request.POST.get('fees_due', 450.00)

        Student.objects.create(
            student_id=student_id,
            name=name,
            student_class=student_class,
            gender=gender,
            fees_due=fees_due
        )
        messages.success(request, f"Student {name} registered successfully!")
        return redirect('portal:student_directory')

    students = Student.objects.all()
    context = {'students': students, 'active_tab': 'students'}
    return render(request, 'portal/student_directory.html', context)


def grade_portal(request):
    trimester = request.GET.get('trimester', 'Trimester 1')
    
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        subject = request.POST.get('subject')
        class_score = float(request.POST.get('class_score', 0))
        exam_score = float(request.POST.get('exam_score', 0))
        total = class_score + exam_score

        if total >= 80:
            letter_grade = 'A'
        elif total >= 70:
            letter_grade = 'B'
        elif total >= 60:
            letter_grade = 'C'
        elif total >= 50:
            letter_grade = 'D'
        else:
            letter_grade = 'F'

        student = get_object_or_404(Student, student_id=student_id)
        Grade.objects.create(
            student=student,
            subject=subject,
            trimester=trimester,
            class_score=class_score,
            exam_score=exam_score,
            total_score=total,
            grade=letter_grade
        )
        messages.success(request, f"Grade submitted for {student.name} in {subject} ({trimester})")
        return redirect(f"{request.path}?trimester={trimester}")

    students = Student.objects.all()
    grades = Grade.objects.filter(trimester=trimester)
    context = {
        'students': students,
        'grades': grades,
        'selected_trimester': trimester,
        'active_tab': 'grades'
    }
    return render(request, 'portal/grade_portal.html', context)


def fee_admin(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        amount = float(request.POST.get('amount', 0))
        student = get_object_or_404(Student, student_id=student_id)
        
        student.fees_paid += amount
        student.save()
        messages.success(request, f"Payment of GHS {amount:.2f} recorded for {student.name}.")
        return redirect('portal:fee_admin')

    students = Student.objects.all()
    context = {'students': students, 'active_tab': 'fees'}
    return render(request, 'portal/fee_admin.html', context)


def promotion_management(request):
    class_order = ["Basic 1", "Basic 2", "Basic 3", "Basic 4", "Basic 5", "Basic 6", "JHS 1", "JHS 2", "JHS 3", "Graduated"]

    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        student = get_object_or_404(Student, student_id=student_id)
        
        if student.student_class in class_order and student.student_class != "Graduated":
            curr_idx = class_order.index(student.student_class)
            student.student_class = class_order[curr_idx + 1]
            student.promoted = True
            student.save()
            messages.success(request, f"{student.name} promoted to {student.student_class}!")
        return redirect('portal:promotion_management')

    students = Student.objects.all()
    context = {'students': students, 'active_tab': 'promotion'}
    return render(request, 'portal/promotion_management.html', context)