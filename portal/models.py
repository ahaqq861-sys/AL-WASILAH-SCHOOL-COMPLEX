from django.db import models
from django.contrib.auth.models import User

class SchoolBranding(models.Model):
    school_name = models.CharField(max_length=200, default="AL-WASILAH SCHOOL COMPLEX")
    tagline = models.CharField(max_length=255, default="Excellence in Knowledge & Character")
    logo = models.ImageField(upload_to='school_branding/', blank=True, null=True)
    primary_color = models.CharField(max_length=10, default="#722F37", help_text="Hex Code for Wine Theme")
    secondary_color = models.CharField(max_length=10, default="#4A1F24", help_text="Darker Wine for headers/accents")
    phone_number = models.CharField(max_length=30, default="+233 20 000 0000")
    email_address = models.EmailField(default="info@alwasilah.edu.gh")
    address = models.TextField(default="Tamale, Northern Region, Ghana")

    class Meta:
        verbose_name = "School Branding Configuration"
        verbose_name_plural = "School Branding Configurations"

    def __str__(self):
        return self.school_name

    @classmethod
    def get_config(cls):
        try:
            config, created = cls.objects.get_or_create(id=1)
            return config
        except Exception:
            return cls(
                school_name="AL-WASILAH SCHOOL COMPLEX",
                tagline="Excellence in Knowledge & Character",
                primary_color="#722F37",
                secondary_color="#4A1F24",
                phone_number="+233 20 000 0000",
                email_address="info@alwasilah.edu.gh",
                address="Tamale, Northern Region, Ghana"
            )


class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    employee_id = models.CharField(max_length=30, unique=True)
    assigned_class = models.CharField(max_length=100, blank=True, null=True, help_text="e.g. Basic 7 Gold")
    subject_specialization = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return f"Teacher: {self.user.get_full_name() or self.user.username} ({self.employee_id})"


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=30, unique=True)
    current_class = models.CharField(max_length=100, default="Unassigned")
    guardian_contact = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self):
        return f"Student: {self.user.get_full_name() or self.user.username} ({self.student_id})"


class GradeRecord(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='grades')
    subject = models.CharField(max_length=100)
    class_score = models.FloatField(default=0.0, help_text="Score out of 30 or 40")
    exam_score = models.FloatField(default=0.0, help_text="Score out of 60 or 70")
    term = models.CharField(max_length=20, default="Term 1")
    academic_year = models.CharField(max_length=20, default="2025/2026")
    teacher_remarks = models.TextField(blank=True, null=True)

    @property
    def total_score(self):
        return self.class_score + self.exam_score

    def __str__(self):
        return f"{self.student.user.username} - {self.subject}: {self.total_score}"


class ClassSchedule(models.Model):
    class_name = models.CharField(max_length=100)
    day_of_week = models.CharField(max_length=20, choices=[
        ('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'), ('Friday', 'Friday')
    ])
    subject = models.CharField(max_length=100)
    time_slot = models.CharField(max_length=50, help_text="e.g. 08:00 AM - 09:00 AM")
    teacher_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.class_name} - {self.day_of_week} - {self.subject}"


class AttendanceRecord(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=[('Present', 'Present'), ('Absent', 'Absent'), ('Late', 'Late')])

    def __str__(self):
        return f"{self.student.user.username} - {self.date}: {self.status}"