from django.db import models
from apps.students.models import Student

class PredictionModel(models.Model):
    name = models.CharField(max_length=100)
    version = models.CharField(max_length=20)
    algorithm = models.CharField(max_length=50)
    accuracy = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    model_file_path = models.CharField(max_length=500)
    
    def __str__(self):
        return f"{self.name} v{self.version} ({self.accuracy:.2%})"

class DropoutPrediction(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    model = models.ForeignKey(PredictionModel, on_delete=models.CASCADE)
    prediction_date = models.DateTimeField(auto_now_add=True)
    dropout_probability = models.FloatField()
    risk_factors = models.JSONField()  # Store contributing factors
    confidence_score = models.FloatField()
    
    class Meta:
        ordering = ['-prediction_date']
    
    def __str__(self):
        return f"{self.student.roll_number} - {self.dropout_probability:.2%} risk"

class StudentAnalytics(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    
    # Attendance Analytics
    overall_attendance_percentage = models.FloatField(default=0)
    attendance_trend = models.CharField(max_length=20, default='stable')  # improving, declining, stable
    consecutive_absences = models.IntegerField(default=0)
    
    # Academic Analytics
    overall_gpa = models.FloatField(default=0)
    academic_trend = models.CharField(max_length=20, default='stable')
    failing_subjects_count = models.IntegerField(default=0)
    
    # Behavioral Analytics
    late_submissions = models.IntegerField(default=0)
    disciplinary_actions = models.IntegerField(default=0)
    
    # Financial Analytics
    fee_payment_history = models.JSONField(default=dict)
    overdue_payments = models.IntegerField(default=0)
    
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Analytics for {self.student.roll_number}"