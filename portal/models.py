from django.db import models
from django.contrib.auth.models import User

class ClassSection(models.Model):
    class_name = models.CharField(max_length=50)
    section_name = models.CharField(max_length=50)
    academic_year = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.class_name} - {self.section_name}"

class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"

class Student(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female')]
    student_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    current_class = models.ForeignKey(ClassSection, on_delete=models.SET_NULL, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    parent_phone = models.CharField(max_length=20)
    enrollment_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.student_id})"

class SubjectResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='results')
    subject_name = models.CharField(max_length=100)
    class_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    exam_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    total_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    grade = models.CharField(max_length=2, blank=True)

    def save(self, *args, **kwargs):
        self.total_score = self.class_score + self.exam_score
        if self.total_score >= 80:
            self.grade = 'A'
        elif self.total_score >= 70:
            self.grade = 'B'
        elif self.total_score >= 60:
            self.grade = 'C'
        elif self.total_score >= 50:
            self.grade = 'D'
        else:
            self.grade = 'F'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} - {self.subject_name}"