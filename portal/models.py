from django.db import models

class ClassLevel(models.Model):
    name = models.CharField(max_length=50, unique=True)  # e.g., Basic 1, JHS 1
    order = models.PositiveIntegerField(default=1)       # For promotion sequence

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name


class AcademicTerm(models.Model):
    TRIMESTER_CHOICES = [
        ('Trimester 1', 'Trimester 1'),
        ('Trimester 2', 'Trimester 2'),
        ('Trimester 3', 'Trimester 3'),
    ]
    year = models.CharField(max_length=20)               # e.g., "2025/2026"
    trimester = models.CharField(max_length=20, choices=TRIMESTER_CHOICES, default='Trimester 1')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.year} - {self.trimester}"


class TeacherProfile(models.Model):
    staff_id = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=100)
    assigned_class = models.ForeignKey(ClassLevel, on_delete=models.SET_NULL, null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.staff_id} - {self.full_name}"


class StudentProfile(models.Model):
    GENDER_CHOICES = [('Male', 'Male'), ('Female', 'Female')]

    student_id = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=100)
    current_class = models.ForeignKey(ClassLevel, on_delete=models.CASCADE, related_name='students')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    is_promoted = models.BooleanField(default=False)

    def total_fees_due(self):
        return sum(f.amount_due for f in self.fee_records.all())

    def total_fees_paid(self):
        return sum(f.amount_paid for f in self.fee_records.all())

    def outstanding_balance(self):
        return self.total_fees_due() - self.total_fees_paid()

    def __str__(self):
        return f"{self.student_id} - {self.full_name}"


class Grade(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='grades')
    subject = models.CharField(max_length=50)
    term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE, related_name='grades')
    class_score = models.FloatField(default=0.0)  # Max 30
    exam_score = models.FloatField(default=0.0)   # Max 70
    total_score = models.FloatField(default=0.0)
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
        return f"{self.student.full_name} - {self.subject} ({self.term})"


class FeeRecord(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='fee_records')
    term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE, related_name='fee_records')
    amount_due = models.DecimalField(max_digits=10, decimal_places=2, default=450.00)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    @property
    def balance(self):
        return self.amount_due - self.amount_paid

    def __str__(self):
        return f"{self.student.full_name} - {self.term}"