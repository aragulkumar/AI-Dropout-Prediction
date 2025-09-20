from django.db import models
from apps.students.models import Student

class NotificationTemplate(models.Model):
    TEMPLATE_TYPES = [
        ('risk_alert', 'Risk Alert'),
        ('attendance_warning', 'Attendance Warning'),
        ('fee_reminder', 'Fee Reminder'),
        ('academic_alert', 'Academic Alert'),
    ]
    
    name = models.CharField(max_length=100)
    template_type = models.CharField(max_length=50, choices=TEMPLATE_TYPES)
    message_template = models.TextField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} ({self.template_type})"

class Notification(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('delivered', 'Delivered'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    template = models.ForeignKey(NotificationTemplate, on_delete=models.CASCADE)
    recipient_phone = models.CharField(max_length=15)
    message_content = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivery_status = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return f"Notification to {self.recipient_phone} - {self.status}"

# SMS Service
class SMSService:
    def __init__(self):
        from twilio.rest import Client
        from django.conf import settings
        
        self.client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
        self.from_number = settings.TWILIO_PHONE_NUMBER
    
    def send_sms(self, to_number, message):
        """Send SMS using Twilio"""
        try:
            message_instance = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )
            
            return {
                'success': True,
                'message_sid': message_instance.sid,
                'status': message_instance.status
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_risk_alert(self, student, risk_level):
        """Send risk level alert to parents"""
        try:
            template = NotificationTemplate.objects.get(
                template_type='risk_alert',
                is_active=True
            )
            
            message = template.message_template.format(
                student_name=student.user.get_full_name(),
                risk_level=risk_level.upper(),
                school_name="Your School Name"
            )
            
            # Send to parent
            result = self.send_sms(student.parent_phone, message)
            
            # Create notification record
            notification = Notification.objects.create(
                student=student,
                template=template,
                recipient_phone=student.parent_phone,
                message_content=message,
                status='sent' if result['success'] else 'failed'
            )
            
            if result['success']:
                notification.sent_at = timezone.now()
                notification.delivery_status = result['status']
                notification.save()
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}