import os
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages
from twilio.rest import Client
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from .models import Student, SubjectResult

# SMS Notification View
def send_result_sms(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    results = SubjectResult.objects.filter(student=student)
    
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    from_number = os.getenv('TWILIO_PHONE_NUMBER')

    summary = ", ".join([f"{r.subject_name}: {r.grade}" for r in results])
    body_text = f"Dear Parent, Terminal Result for {student.first_name}: {summary}. Thank you."

    if account_sid and auth_token:
        try:
            client = Client(account_sid, auth_token)
            client.messages.create(
                body=body_text,
                from_=from_number,
                to=student.parent_phone
            )
            messages.success(request, f"SMS sent to {student.parent_phone}")
        except Exception as e:
            messages.error(request, f"SMS Error: {str(e)}")
    else:
        messages.warning(request, "SMS credentials missing in environment settings.")
        
    return redirect('admin:portal_student_changelist')

# PDF Report Generation View
def generate_student_pdf(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    results = SubjectResult.objects.filter(student=student)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{student.student_id}_report.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 750, "AL-WASILAH SCHOOL COMPLEX")
    p.setFont("Helvetica", 12)
    p.drawString(100, 730, f"Official Terminal Report - {student.first_name} {student.last_name}")
    p.drawString(100, 715, f"Student ID: {student.student_id} | Class: {student.current_class}")

    p.line(100, 700, 500, 700)

    y = 670
    p.setFont("Helvetica-Bold", 10)
    p.drawString(100, y, "Subject")
    p.drawString(250, y, "Class Score")
    p.drawString(330, y, "Exam Score")
    p.drawString(410, y, "Total")
    p.drawString(470, y, "Grade")

    p.setFont("Helvetica", 10)
    for res in results:
        y -= 20
        p.drawString(100, y, str(res.subject_name))
        p.drawString(250, y, str(res.class_score))
        p.drawString(330, y, str(res.exam_score))
        p.drawString(410, y, str(res.total_score))
        p.drawString(470, y, str(res.grade))

    p.showPage()
    p.save()
    return response