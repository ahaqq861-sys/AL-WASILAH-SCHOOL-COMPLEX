import uuid
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

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

class SchoolBranding(models.Model):
    # Basic School Info
    school_name = models.CharField(max_length=255, default='Al-Wasilah School Complex')
    logo_text = models.CharField(max_length=255, default='Al-Wasilah Portal')
    logo_image = models.ImageField(upload_to='branding/', null=True, blank=True)
    
    # Contact Details (Expanded max_length to allow multiple phone numbers & long addresses)
    contact_email = models.EmailField(max_length=255, default='info@alwasilah.edu.gh')
    contact_phone = models.CharField(max_length=100, default='+233 20 000 0000')
    address = models.CharField(max_length=255, default='Tamale, Ghana')
    website_url = models.URLField(max_length=255, default='https://alwasilah.edu.gh', blank=True)
    whatsapp_number = models.CharField(max_length=100, default='+233 20 000 0000', blank=True)

    # Color Theme Customization
    primary_color = models.CharField(max_length=20, default='#581c87')
    secondary_color = models.CharField(max_length=20, default='#2e1065')
    accent_color = models.CharField(max_length=20, default='#eab308')

    # Advanced Branding Features
    banner_announcement = models.CharField(max_length=500, default='Welcome to the official Al-Wasilah Portal!', blank=True)
    enable_top_banner = models.BooleanField(default=True)
    footer_copyright = models.CharField(max_length=255, default='© 2026 Al-Wasilah School Complex. All Rights Reserved.', blank=True)
    
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.school_name

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('TEACHER', 'Teacher / Lecturer'),
        ('STUDENT', 'Student'),
        ('PARENT', 'Parent / Guardian'),
    ]
    SEX_CHOICES = [
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
    ]
    STUDY_STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('GRADUATED', 'Graduated'),
        ('SUSPENDED', 'Suspended'),
        ('WITHDRAWN', 'Withdrawn'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='STUDENT')
    index_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    
    # Personal Details
    date_of_birth = models.DateField(null=True, blank=True)
    sex = models.CharField(max_length=10, choices=SEX_CHOICES, default='MALE')
    gender = models.CharField(max_length=20, default='Male')
    phone_number = models.CharField(max_length=50, blank=True)
    passport_picture = models.ImageField(upload_to='passports/', null=True, blank=True)
    study_status = models.CharField(max_length=20, choices=STUDY_STATUS_CHOICES, default='ACTIVE')
    
    # Class & Course Relationships
    assigned_class = models.ForeignKey(ClassLevel, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_students')
    assigned_courses = models.ManyToManyField(Course, blank=True, related_name='assigned_teachers')
    children = models.ManyToManyField(User, blank=True, related_name='guardians')

    # Student Guardian Details
    guardian_name = models.CharField(max_length=150, blank=True)
    guardian_phone = models.CharField(max_length=50, blank=True)
    guardian_email = models.EmailField(blank=True)
    guardian_relationship = models.CharField(max_length=50, blank=True)

    def save(self, *args, **kwargs):
        if not self.index_number:
            prefix = "STU" if self.role == "STUDENT" else "TCH" if self.role == "TEACHER" else "USR"
            self.index_number = f"{prefix}/{uuid.uuid4().hex[:6].upper()}/26"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.index_number})"

class AcademicTerm(models.Model):
    TRIMESTER_CHOICES = [
        ('Trimester 1', 'Trimester 1'),
        ('Trimester 2', 'Trimester 2'),
        ('Trimester 3', 'Trimester 3'),
    ]
    year = models.CharField(max_length=20, default='2026/2027')
    trimester = models.CharField(max_length=50, default='Trimester 1')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.year} - {self.trimester}"

class Grade(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grades')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    grade_letter = models.CharField(max_length=5, default='A')
    teacher_remark = models.TextField(blank=True, default='Good performance.')

    def __str__(self):
        return f"{self.student.username} - {self.course.name} ({self.term.trimester})"

class FeeRecord(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fees')
    term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    @property
    def balance_due(self):
        return self.amount_due - self.amount_paid

    def __str__(self):
        return f"{self.student.username} - {self.term.trimester} Fee"

class PaymentTransaction(models.Model):
    fee_record = models.ForeignKey(FeeRecord, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    receipt_number = models.CharField(max_length=50, unique=True)
    payment_method = models.CharField(max_length=50, default='Mobile Money / Cash')
    created_at = models.DateTimeField(auto_now_add=True)

class Attendance(models.Model):
    STATUS_CHOICES = [('PRESENT', 'Present'), ('ABSENT', 'Absent'), ('LATE', 'Late')]
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PRESENT')
    term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('student', 'date')

class TimetableSchedule(models.Model):
    DAY_CHOICES = [('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), ('Friday', 'Friday')]
    class_level = models.ForeignKey(ClassLevel, on_delete=models.CASCADE, related_name='schedules')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    day = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()

class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    target_class = models.ForeignKey(ClassLevel, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

# --------------------------------------------------------------------------
# Django Signal: Safely Assign ADMIN Role to Superusers
# --------------------------------------------------------------------------
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        role = 'ADMIN' if instance.is_superuser else 'STUDENT'
        UserProfile.objects.get_or_create(user=instance, defaults={'role': role})
    else:
        if instance.is_superuser and hasattr(instance, 'profile'):
            if instance.profile.role != 'ADMIN':
                instance.profile.role = 'ADMIN'
                instance.profile.save()