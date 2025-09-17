from django.db import models
from apps.students.models import Student

class PredictionModel(models.Model):
    name = models.CharField(max_length=100)
    version = models.CharField(max_length=20)
    algorithm = models.CharField(max_length=100)
    accuracy = models.FloatField()
    precision = models.FloatField()
    recall = models.FloatField()
    f1_score = models.FloatField()
    model_file_path = models.CharField(max_length=500)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} v{self.version} - {self.accuracy:.2%} accuracy"

class DropoutPrediction(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    model = models.ForeignKey(PredictionModel, on_delete=models.CASCADE)
    prediction_date = models.DateTimeField(auto_now_add=True)
    dropout_probability = models.FloatField()
    risk_factors = models.JSONField(default=dict)
    confidence_score = models.FloatField()
    
    class Meta:
        ordering = ['-prediction_date']
        unique_together = ['student', 'model', 'prediction_date']
    
    def __str__(self):
        return f"{self.student.roll_number} - {self.dropout_probability:.2%} risk"

class StudentAnalytics(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    
    # Attendance metrics
    overall_attendance_percentage = models.FloatField(default=0.0)
    attendance_trend = models.CharField(
        max_length=20,
        choices=[
            ('improving', 'Improving'),
            ('declining', 'Declining'),
            ('stable', 'Stable'),
        ],
        default='stable'
    )
    consecutive_absences = models.IntegerField(default=0)
    
    # Academic metrics
    overall_gpa = models.FloatField(default=0.0)
    academic_trend = models.CharField(
        max_length=20,
        choices=[
            ('improving', 'Improving'),
            ('declining', 'Declining'),
            ('stable', 'Stable'),
        ],
        default='stable'
    )
    failing_subjects_count = models.IntegerField(default=0)
    
    # Behavioral metrics
    late_submissions = models.IntegerField(default=0)
    disciplinary_actions = models.IntegerField(default=0)
    
    # Financial metrics
    fee_payment_history = models.JSONField(default=dict)
    overdue_payments_count = models.IntegerField(default=0)
    
    # Risk factors
    engagement_score = models.FloatField(default=0.0)
    social_indicators = models.JSONField(default=dict)
    
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Analytics for {self.student.roll_number}"