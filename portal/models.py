from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

ROLE_CHOICES = (
    ('admin', 'Admin'),
    ('teacher', 'Teacher'),
    ('student', 'Student'),
)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class SchoolBranding(models.Model):
    school_name = models.CharField(max_length=255, default='Al-Wasilah School Complex')
    primary_color = models.CharField(max_length=20, default='#800020')
    secondary_color = models.CharField(max_length=20, default='#1A252C')
    tagline = models.CharField(max_length=255, default='Knowledge and Virtue')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email_address = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.school_name

class StudentGrade(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grades')
    subject = models.CharField(max_length=100)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    term = models.CharField(max_length=50, default='Term 1')
    date_recorded = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.subject}: {self.score}"

class FeePayment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fee_payments')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    total_fee = models.DecimalField(max_digits=10, decimal_places=2)
    date_paid = models.DateField(auto_now_add=True)

    @property
    def balance(self):
        return self.total_fee - self.amount_paid

    def __str__(self):
        return f"{self.student.username} - Paid: {self.amount_paid}"

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        role = 'admin' if instance.is_superuser else 'student'
        UserProfile.objects.get_or_create(user=instance, defaults={'role': role})
    else:
        if hasattr(instance, 'userprofile'):
            instance.userprofile.save()