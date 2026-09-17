from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

ROLE_CHOICES = (
    ('admin', 'Admin'),
    ('teacher', 'Teacher'),
    ('student', 'Student'),
)

SEX_CHOICES = (
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'),
)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    
    # Personal Identification Fields
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    sex = models.CharField(max_length=10, choices=SEX_CHOICES, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    passport_photo = models.ImageField(upload_to='passports/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Permissions
    can_edit_branding = models.BooleanField(default=False)
    is_first_login = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} ({self.role.upper()})"

class SchoolBranding(models.Model):
    school_name = models.CharField(max_length=255, default='Al-Wasilah School Complex')
    tagline = models.CharField(max_length=255, default='Knowledge and Virtue')
    logo = models.ImageField(upload_to='school_branding/', blank=True, null=True)
    primary_color = models.CharField(max_length=20, default='#800020')
    secondary_color = models.CharField(max_length=20, default='#1A252C')
    
    # School Contact Information
    phone_number = models.CharField(max_length=20, default='+233 00 000 0000')
    email_address = models.EmailField(default='info@alwasilah.edu.gh')
    address = models.TextField(default='P.O. Box 123, School Location')

    def __str__(self):
        return self.school_name

class StudentGrade(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grades')
    subject = models.CharField(max_length=100)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    term = models.CharField(max_length=50, default='Term 1')
    date_recorded = models.DateField(auto_now_add=True)

class FeePayment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fee_payments')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    total_fee = models.DecimalField(max_digits=10, decimal_places=2)
    date_paid = models.DateField(auto_now_add=True)

    @property
    def balance(self):
        return self.total_fee - self.amount_paid

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        role = 'admin' if instance.is_superuser else 'student'
        can_edit = True if instance.is_superuser else False
        UserProfile.objects.get_or_create(
            user=instance, 
            defaults={
                'role': role, 
                'can_edit_branding': can_edit,
                'is_first_login': False if instance.is_superuser else True
            }
        )