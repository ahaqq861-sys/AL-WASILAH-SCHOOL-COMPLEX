from django.db import models
from django.contrib.auth.models import User

class ClassLevel(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Course(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    class_level = models.ForeignKey(ClassLevel, on_delete=models.CASCADE, related_name='courses')

    def __str__(self):
        return f"{self.name} ({self.class_level.name})"

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('TEACHER', 'Teacher / Lecturer'),
        ('STUDENT', 'Student'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='STUDENT')
    phone_number = models.CharField(max_length=20, blank=True)
    assigned_class = models.ForeignKey(ClassLevel, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_students')
    assigned_courses = models.ManyToManyField(Course, blank=True, related_name='assigned_teachers')

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

class SchoolBranding(models.Model):
    school_name = models.CharField(max_length=255, default='Al-Wasilah School Complex')
    logo_text = models.CharField(max_length=100, default='Al-Wasilah Portal')
    primary_color = models.CharField(max_length=7, default='#581c87')
    secondary_color = models.CharField(max_length=7, default='#2e1065')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.school_name

class AcademicTerm(models.Model):
    TRIMESTER_CHOICES = [
        ('Trimester 1', 'Trimester 1'),
        ('Trimester 2', 'Trimester 2'),
        ('Trimester 3', 'Trimester 3'),
    ]
    year = models.CharField(max_length=20, default='2026/2027')
    trimester = models.CharField(max_length=20, choices=TRIMESTER_CHOICES, default='Trimester 1')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.year} - {self.trimester}"

class Grade(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grades')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    grade_letter = models.CharField(max_length=5, default='A')

    def __str__(self):
        return f"{self.student.username} - {self.course.name} ({self.term.trimester})"

class FeeRecord(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fees')
    term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    @property
    def is_fully_paid(self):
        return self.amount_paid >= self.amount_due

    def __str__(self):
        return f"{self.student.username} - {self.term.trimester} Fee"