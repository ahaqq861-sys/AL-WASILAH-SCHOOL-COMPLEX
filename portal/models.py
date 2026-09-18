from django.db import models
from django.contrib.auth.models import User

class ClassLevel(models.Model):
    name = models.CharField(max_length=50, unique=True) # e.g., Basic 1, JHS 1
    numeric_order = models.IntegerField(default=1) # Used to order classes for promotion
    next_class = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='previous_class')

    class Meta:
        ordering = ['numeric_order']

    def __str__(self):
        return self.name

class AcademicTerm(models.Model):
    TRIMESTER_CHOICES = [
        ('Trimester 1', 'Trimester 1'),
        ('Trimester 2', 'Trimester 2'),
        ('Trimester 3', 'Trimester 3'),
    ]
    academic_year = models.CharField(max_length=20) # e.g., 2026/2027
    trimester = models.CharField(max_length=20, choices=TRIMESTER_CHOICES)
    is_current = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_current:
            AcademicTerm.objects.filter(is_current=True).exclude(pk=self.pk).update(is_current=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.academic_year} - {self.trimester}"

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, unique=True)
    current_class = models.ForeignKey(ClassLevel, on_delete=models.SET_NULL, null=True, blank=True)
    is_graduated = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.current_class})"

class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    assigned_classes = models.ManyToManyField(ClassLevel, blank=True)

    def __str__(self):
        return self.user.get_full_name()

class Grade(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)
    subject_name = models.CharField(max_length=100)
    score = models.DecimalField(max_digits=5, decimal_places=2)

class FeeRecord(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    @property
    def balance(self):
        return self.amount_due - self.amount_paid