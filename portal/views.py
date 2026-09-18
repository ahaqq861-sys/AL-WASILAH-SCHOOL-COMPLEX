from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import StudentProfile, Grade, FeeRecord, ClassLevel, AcademicTerm

def dashboard(request):
    active_term = AcademicTerm.objects.filter(is_active=True).first()
    students = StudentProfile.objects.all()
    
    total_students = students.count()
    fee_records = FeeRecord.objects.all()
    total_due = sum(f.amount_due for f in fee_records)
    total_paid = sum(f.amount_paid for f in fee_records)
    balance = total_due - total_paid

    context = {
        'active_term': active_term,
        'total_students': total_students,
        'total_due': total_due,
        'total_paid': total_paid,
        'balance': balance,
    }
    return render(request, 'portal/dashboard.html', context)


def student_directory(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        full_name = request.POST.get('full_name')
        class_id = request.POST.get('class_id')
        gender = request.POST.get('gender')

        current_class = get_object_or_404(ClassLevel, id=class_id)
        student = StudentProfile.objects.create(
            student_id=student_id,
            full_name=full_name,
            current_class=current_class,
            gender=gender
        )

        active_term = AcademicTerm.objects.filter(is_active=True).first()
        if active_term:
            FeeRecord.objects.create(student=student, term=active_term, amount_due=450.00, amount_paid=0.00)

        messages.success(request, f"Student {full_name} registered successfully!")
        return redirect('portal:student_directory')

    students = StudentProfile.objects.select_related('current_class').all()
    classes = ClassLevel.objects.all()
    return render(request, 'portal/student_directory.html', {'students': students, 'classes': classes})


def grade_portal(request):
    active_term = AcademicTerm.objects.filter(is_active=True).first()

    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        subject = request.POST.get('subject')
        class_score = float(request.POST.get('class_score', 0))
        exam_score = float(request.POST.get('exam_score', 0))

        student = get_object_or_404(StudentProfile, id=student_id)
        Grade.objects.create(
            student=student,
            subject=subject,
            term=active_term,
            class_score=class_score,
            exam_score=exam_score
        )
        messages.success(request, f"Grade recorded for {student.full_name} in {subject}.")
        return redirect('portal:grade_portal')

    grades = Grade.objects.filter(term=active_term) if active_term else Grade.objects.none()
    students = StudentProfile.objects.all()
    return render(request, 'portal/grade_portal.html', {'grades': grades, 'students': students, 'active_term': active_term})


def fee_admin(request):
    if request.method == 'POST':
        fee_record_id = request.POST.get('fee_record_id')
        payment_amount = float(request.POST.get('amount', 0))

        fee_record = get_object_or_404(FeeRecord, id=fee_record_id)
        fee_record.amount_paid += payment_amount
        fee_record.save()

        messages.success(request, f"Recorded GHS {payment_amount:.2f} payment for {fee_record.student.full_name}.")
        return redirect('portal:fee_admin')

    fee_records = FeeRecord.objects.select_related('student', 'term').all()
    return render(request, 'portal/fee_admin.html', {'fee_records': fee_records})


def promotion_management(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        student = get_object_or_404(StudentProfile, id=student_id)
        
        next_class = ClassLevel.objects.filter(order__gt=student.current_class.order).order_by('order').first()
        if next_class:
            student.current_class = next_class
            student.is_promoted = True
            student.save()
            messages.success(request, f"{student.full_name} promoted to {next_class.name}!")
        else:
            messages.warning(request, f"{student.full_name} is already in the highest available class level.")

        return redirect('portal:promotion_management')

    students = StudentProfile.objects.select_related('current_class').all()
    return render(request, 'portal/promotion.html', {'students': students})