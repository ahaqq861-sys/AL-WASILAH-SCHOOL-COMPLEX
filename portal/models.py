from django.db import models

class Student(models.Model):
    student_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    student_class = models.CharField(max_length=20)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    fees_due = models.DecimalField(max_digits=10, decimal_places=2, default=450.00)
    fees_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    promoted = models.BooleanField(default=False)

    def balance(self):
        return self.fees_due - self.fees_paid

    def __str__(self):
        return f"{self.student_id} - {self.name}"


class Grade(models.Model):
    TRIMESTER_CHOICES = [
        ('Trimester 1', 'Trimester 1'),
        ('Trimester 2', 'Trimester 2'),
        ('Trimester 3', 'Trimester 3'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grades')
    subject = models.CharField(max_length=50)
    trimester = models.CharField(max_length=20, choices=TRIMESTER_CHOICES, default='Trimester 1')
    class_score = models.FloatField(default=0.0)
    exam_score = models.FloatField(default=0.0)
    total_score = models.FloatField(default=0.0)
    grade = models.CharField(max_length=2)

    def __str__(self):
        return f"{self.student.name} - {self.subject} ({self.trimester})"