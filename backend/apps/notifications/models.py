from django.db import models
from apps.students.models import Student

class NotificationTemplate(models.Model):
    TEMPLATE_TYPE_CHOICES = [
        ('risk_alert', 'Risk Alert'),
        ('attendance_warning', 'Attendance Warning'),
        ('academic_warning', 'Academic Warning'),
        ('fee_reminder', 'Fee Reminder'),
        ('general', 'General'),
    ]
    
    name = models.CharField(max_length=100)
    template_type = models.CharField(max_length=30, choices=TEMPLATE_TYPE_CHOICES)
    subject = models.CharField(max_length=200, blank=True, null=True)
    message_template = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.get_template_type_display()}"

class Notification(models.Model):
    CHANNEL_CHOICES = [
        ('sms', 'SMS'),
        ('email', 'Email'),
        ('push', 'Push Notification'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('delivered', 'Delivered'),
    ]
    
    RECIPIENT_CHOICES = [
        ('student', 'Student'),
        ('guardian', 'Guardian'),
        ('teacher', 'Teacher'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    template = models.ForeignKey(NotificationTemplate, on_delete=models.CASCADE)
    channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES)
    recipient_type = models.CharField(max_length=10, choices=RECIPIENT_CHOICES)
    recipient_contact = models.CharField(max_length=100)
    
    subject = models.CharField(max_length=200, blank=True, null=True)
    message_content = models.TextField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, null=True)
    
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.roll_number} - {self.template.name} - {self.status}"

class AlertLog(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=50)
    severity = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical'),
        ]
    )
    message = models.TextField()
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.roll_number} - {self.alert_type} - {self.severity}"