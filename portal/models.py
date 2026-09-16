from django.db import models
from django.contrib.auth.models import User

class SchoolBranding(models.Model):
    school_name = models.CharField(max_length=200, default="Al-Wasilah School Complex")
    logo = models.ImageField(upload_to='school_logos/', null=True, blank=True)
    primary_color = models.CharField(max_length=20, default="#800020")

    def __str__(self):
        return self.school_name

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Administrator'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    must_change_password = models.BooleanField(default=True)
    
    # Specific fields
    student_id = models.CharField(max_length=50, null=True, blank=True)
    current_class = models.CharField(max_length=50, null=True, blank=True)
    guardian_contact = models.CharField(max_length=50, null=True, blank=True)
    subject_assigned = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"