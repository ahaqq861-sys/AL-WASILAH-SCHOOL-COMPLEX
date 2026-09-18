from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('TEACHER', 'Teacher / Lecturer'),
        ('STUDENT', 'Student'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='STUDENT')
    phone_number = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

class SchoolBranding(models.Model):
    school_name = models.CharField(max_length=255, default='Al-Wasilah School Complex')
    logo_text = models.CharField(max_length=100, default='Al-Wasilah Portal')
    primary_color = models.CharField(max_length=7, default='#581c87') # Wine Header
    secondary_color = models.CharField(max_length=7, default='#2e1065') # Wine Sidebar
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.school_name

class PendingModification(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='modifications')
    title = models.CharField(max_length=200)
    description = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.teacher.username}"