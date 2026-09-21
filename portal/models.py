from django.db import models
from django.contrib.auth.models import User

# --- BRANDING & ACADEMIC STRUCTURE ---
class SchoolBranding(models.Model):
    school_name = models.CharField(max_length=255, default="Al-Wasilah School Complex")
    logo_image = models.ImageField(upload_to="branding/", blank=True, null=True)
    logo_text = models.CharField(max_length=100, blank=True, null=True)
    primary_color = models.CharField(max_length=20, default="#800020")
    secondary_color = models.CharField(max_length=20, default="#ffffff")
    accent_color = models.CharField(max_length=20, default="#d4af37")
    current_academic_year = models.CharField(max_length=20, default="2026/2027")
    current_term = models.CharField(max_length=50, default="Trimester 1")
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=30, blank=True, null=True)
    whatsapp_number = models.CharField(max_length=30, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    enable_top_banner = models.BooleanField(default=False)
    banner_announcement = models.CharField(max_length=255, blank=True, null=True)
    footer_copyright = models.CharField(max_length=255, default="Al-Wasilah School Complex. All rights reserved.")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.school_name

class AcademicClass(models.Model):
    name = models.CharField(max_length=50, unique=True) # e.g., Basic 7, Basic 8

    def __str__(self):
        return self.name

# Alias for backwards compatibility with previous migrations/models
ClassLevel = AcademicClass

class AcademicTerm(models.Model):
    name = models.CharField(max_length=50) # e.g., Trimester 1
    academic_year = models.CharField(max_length=20)
    is_current = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.academic_year})"

# --- USER PROFILES ---
class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('TEACHER', 'Teacher'),
        ('STUDENT', 'Student'),
        ('PARENT', 'Parent'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='STUDENT')
    index_number = models.CharField(max_length=50, blank=True, null=True, unique=True)
    assigned_class = models.ForeignKey(AcademicClass, on_delete=models.SET_NULL, blank=True, null=True)
    assigned_courses = models.ManyToManyField('Course', blank=True)
    children = models.ManyToManyField('self', symmetrical=False, blank=True, limit_choices_to={'role': 'STUDENT'})
    passport_picture = models.ImageField(upload_to="profiles/", blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    sex = models.CharField(max_length=10, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    guardian_name = models.CharField(max_length=100, blank=True, null=True)
    guardian_phone = models.CharField(max_length=20, blank=True, null=True)
    guardian_email = models.EmailField(blank=True, null=True)
    guardian_relationship = models.CharField(max_length=50, blank=True, null=True)
    study_status = models.CharField(max_length=20, default="ACTIVE")

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.role})"

# --- ACADEMICS, SUBJECTS & TIMETABLES ---
class Course(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    class_level = models.ForeignKey(AcademicClass, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

class SubjectCourse(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    academic_class = models.ForeignKey(AcademicClass, on_delete=models.CASCADE, related_name="courses")
    term = models.CharField(max_length=50, default="Trimester 1")

    def __str__(self):
        return f"{self.name} ({self.academic_class.name})"

class TimetableSchedule(models.Model):
    class_level = models.ForeignKey(AcademicClass, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=15)
    time_slot = models.CharField(max_length=50)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.class_level.name} - {self.day_of_week} ({self.course.name})"

class TimetableEntry(models.Model):
    academic_class = models.ForeignKey(AcademicClass, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=15)
    time_slot = models.CharField(max_length=50)
    subject = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.academic_class.name} - {self.day_of_week} ({self.subject})"

class Grade(models.Model):
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE, limit_choices_to={'role': 'STUDENT'})
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)
    class_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    exam_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    @property
    def total_score(self):
        return self.class_score + self.exam_score

    def __str__(self):
        return f"{self.student.user.username} - {self.course.name}"

class Attendance(models.Model):
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE, limit_choices_to={'role': 'STUDENT'})
    date = models.DateField()
    term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=(('PRESENT', 'Present'), ('ABSENT', 'Absent'), ('LATE', 'Late')))

    class Meta:
        unique_together = ('student', 'date')

# --- FINANCIALS & LEDGERS ---
class FeeRecord(models.Model):
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE, limit_choices_to={'role': 'STUDENT'})
    term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)
    total_due = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    @property
    def balance(self):
        return self.total_due - self.amount_paid

    def __str__(self):
        return f"{self.student.user.username} - Fees"

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

class PaymentTransaction(models.Model):
    fee_record = models.ForeignKey(FeeRecord, on_delete=models.CASCADE, related_name="transactions")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    reference = models.CharField(max_length=100, unique=True)
    payment_method = models.CharField(max_length=50, default="Mobile Money")

# --- ANNOUNCEMENTS & EVENTS ---
class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    target_class = models.ForeignKey(AcademicClass, on_delete=models.SET_NULL, null=True, blank=True)

class AcademicEvent(models.Model):
    title = models.CharField(max_length=200)
    event_date = models.DateField()
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.title} - {self.event_date}"