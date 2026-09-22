from django.db import models
from django.contrib.auth.models import User

class SchoolBranding(models.Model):
    school_name = models.CharField(max_length=255, default="Al-Wasilah School Complex")
    logo_image = models.ImageField(upload_to='branding/', blank=True, null=True)
    logo_text = models.CharField(max_length=100, default="AL-WASILAH")
    primary_color = models.CharField(max_length=20, default="#1E3A8A")
    secondary_color = models.CharField(max_length=20, default="#0D9488")
    accent_color = models.CharField(max_length=20, default="#F59E0B")
    current_academic_year = models.CharField(max_length=20, default="2025/2026")
    current_term = models.CharField(max_length=20, default="Term 1")
    contact_email = models.EmailField(blank=True, default="info@alwasilah.edu")
    contact_phone = models.CharField(max_length=20, blank=True, default="+233000000000")
    whatsapp_number = models.CharField(max_length=20, blank=True, default="+233000000000")
    address = models.TextField(blank=True, default="Tamale, Ghana")
    website_url = models.URLField(blank=True, default="https://alwasilah.edu")
    enable_top_banner = models.BooleanField(default=True)
    banner_announcement = models.CharField(max_length=255, blank=True, default="Welcome to Al-Wasilah Campus Portal!")
    footer_copyright = models.CharField(max_length=255, default="© 2026 Al-Wasilah School Complex. All Rights Reserved.")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "School Branding"
        verbose_name_plural = "School Branding"

    def __str__(self):
        return self.school_name


class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('ADMIN', 'Administrator'),
        ('TEACHER', 'Teacher'),
        ('STUDENT', 'Student'),
        ('PARENT', 'Parent/Guardian'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='STUDENT')
    phone_number = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


class AcademicClass(models.Model):
    name = models.CharField(max_length=50)  # e.g., Primary 1, JHS 2
    section = models.CharField(max_length=10, blank=True)  # e.g., A, B

    class Meta:
        verbose_name_plural = "Academic Classes"

    def __str__(self):
        return f"{self.name} {self.section}".strip()


class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    index_number = models.CharField(max_length=30, unique=True)
    current_class = models.ForeignKey(AcademicClass, on_delete=models.SET_NULL, null=True, related_name='students')
    guardian_name = models.CharField(max_length=100, blank=True)
    guardian_phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.index_number})"


class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grades')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    academic_year = models.CharField(max_length=20)
    term = models.CharField(max_length=20)
    class_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # 30% or 40%
    exam_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)   # 70% or 60%
    
    @property
    def total_score(self):
        return self.class_score + self.exam_score

    def __str__(self):
        return f"{self.student.index_number} - {self.subject.name}: {self.total_score}"


class FeeLedger(models.Model):
    STATUS_CHOICES = (
        ('PAID', 'Paid'),
        ('PARTIAL', 'Partial'),
        ('OWING', 'Owing'),
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fees')
    academic_year = models.CharField(max_length=20)
    term = models.CharField(max_length=20)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    @property
    def balance(self):
        return self.total_amount - self.amount_paid

    @property
    def status(self):
        if self.amount_paid >= self.total_amount:
            return 'PAID'
        elif self.amount_paid > 0:
            return 'PARTIAL'
        return 'OWING'

    def __str__(self):
        return f"{self.student.index_number} - {self.term} ({self.status})"


class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title