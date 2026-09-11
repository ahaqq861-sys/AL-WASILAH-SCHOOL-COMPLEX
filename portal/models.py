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
        config, created = cls.objects.get_or_create(id=1)
        return config


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