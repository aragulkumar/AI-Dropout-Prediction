from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

class Class(models.Model):
    name = models.CharField(max_length=50)
    grade = models.IntegerField()
    section = models.CharField(max_length=10)
    academic_year = models.CharField(max_length=20)
    
    class Meta:
        unique_together = ['name', 'grade', 'section', 'academic_year']
    
    def __str__(self):
        return f"{self.name} - Grade {self.grade}{self.section}"

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    roll_number = models.CharField(max_length=20, unique=True)
    student_class = models.ForeignKey(Class, on_delete=models.CASCADE)
    admission_date = models.DateField()
    parent_name = models.CharField(max_length=100)
    parent_phone = models.CharField(max_length=15)
    parent_email = models.EmailField(blank=True)
    address = models.TextField()
    
    # Risk Assessment Fields
    current_risk_level = models.CharField(
        max_length=20,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
        default='low'
    )
    risk_score = models.FloatField(default=0.0)
    last_risk_update = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.roll_number} - {self.user.get_full_name()}"

class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    credits = models.IntegerField(default=1)
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(
        max_length=10,
        choices=[('present', 'Present'), ('absent', 'Absent'), ('late', 'Late')]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'subject', 'date']
    
    def __str__(self):
        return f"{self.student.roll_number} - {self.subject.code} - {self.date}"

class Assessment(models.Model):
    ASSESSMENT_TYPES = [
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
        ('midterm', 'Midterm'),
        ('final', 'Final Exam'),
        ('project', 'Project'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    assessment_type = models.CharField(max_length=20, choices=ASSESSMENT_TYPES)
    title = models.CharField(max_length=200)
    max_marks = models.IntegerField()
    obtained_marks = models.IntegerField()
    date_conducted = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.student.roll_number} - {self.title}"
    
    @property
    def percentage(self):
        return (self.obtained_marks / self.max_marks) * 100 if self.max_marks > 0 else 0

class FeeRecord(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    academic_year = models.CharField(max_length=20)
    semester = models.CharField(max_length=20)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    due_date = models.DateField()
    payment_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('paid', 'Paid'), ('overdue', 'Overdue')],
        default='pending'
    )
    
    def __str__(self):
        return f"{self.student.roll_number} - {self.academic_year} - {self.status}"
    
    @property
    def due_amount(self):
        return self.total_amount - self.paid_amount