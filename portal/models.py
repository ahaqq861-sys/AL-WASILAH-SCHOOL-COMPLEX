from django.db import models
from django.contrib.auth.models import User

class SchoolBranding(models.Model):
    school_name = models.CharField(max_length=255, default="Al-Wasilah School Complex")
    logo_image = models.ImageField(upload_to="branding/", blank=True, null=True)
    current_academic_year = models.CharField(max_length=20, default="2026/2027")
    current_term = models.CharField(max_length=50, default="Trimester 1")

    def __str__(self):
        return self.school_name

class AcademicClass(models.Model):
    name = models.CharField(max_length=50, unique=True)  # e.g., Basic 7, Basic 8

    def __str__(self):
        return self.name

class SubjectCourse(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    academic_class = models.ForeignKey(AcademicClass, on_delete=models.CASCADE, related_name="courses")
    term = models.CharField(max_length=50, default="Trimester 1")

    def __str__(self):
        return f"{self.name} ({self.academic_class.name})"

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('TEACHER', 'Teacher'),
        ('STUDENT', 'Student'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='STUDENT')
    index_number = models.CharField(max_length=50, blank=True, null=True, unique=True)
    assigned_class = models.ForeignKey(AcademicClass, on_delete=models.SET_NULL, blank=True, null=True)
    passport_picture = models.ImageField(upload_to="profiles/", blank=True, null=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.role})"

class FeeLedger(models.Model):
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE, limit_choices_to={'role': 'STUDENT'}, related_name="fee_ledgers")
    academic_class = models.ForeignKey(AcademicClass, on_delete=models.CASCADE)
    term = models.CharField(max_length=50, default="Trimester 1")
    total_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def balance_due(self):
        return self.total_fees - self.amount_paid

    def __str__(self):
        return f"{self.student.user.get_full_name() or self.student.user.username} - {self.term}"

class TimetableEntry(models.Model):
    academic_class = models.ForeignKey(AcademicClass, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=15)  # e.g., Monday
    time_slot = models.CharField(max_length=50)    # e.g., 08:00 AM - 09:00 AM
    subject = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.academic_class.name} - {self.day_of_week} ({self.subject})"

class AcademicEvent(models.Model):
    title = models.CharField(max_length=200)
    event_date = models.DateField()
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.title} - {self.event_date}"