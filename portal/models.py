from django.contrib.auth.models import User
from django.db import models


class SchoolBranding(models.Model):
    school_name = models.CharField(
        max_length=255, default="Al-Wasilah School Complex"
    )
    tagline = models.CharField(
        max_length=255, default="Knowledge and Virtue", blank=True, null=True
    )
    logo = models.ImageField(upload_to="branding/logos/", blank=True, null=True)
    primary_color = models.CharField(max_length=7, default="#800020")
    secondary_color = models.CharField(max_length=7, default="#1A252C")

    # Contact Details
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email_address = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.school_name


class TeacherProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="teacher_profile"
    )
    staff_id = models.CharField(max_length=50, unique=True)
    subject_specialization = models.CharField(
        max_length=100, blank=True, null=True
    )
    profile_picture = models.ImageField(
        upload_to="profiles/teachers/", blank=True, null=True
    )

    def __str__(self):
        return f"Teacher: {self.user.get_full_name() or self.user.username}"


class StudentProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="student_profile"
    )
    student_id = models.CharField(max_length=50, unique=True)
    grade_level = models.CharField(max_length=50, blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to="profiles/students/", blank=True, null=True
    )

    def __str__(self):
        return f"Student: {self.user.get_full_name() or self.user.username}"