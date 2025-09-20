from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Notification
from .sms_service import SMSService

@shared_task
def process_pending_notifications():
    """Process all pending SMS notifications"""
    sms_service = SMSService()
    
    pending_notifications = Notification.objects.filter(
        status='pending'
    ).select_related('student', 'template')
    
    for notification in pending_notifications:
        try:
            result = sms_service.send_sms(
                notification.recipient_phone,
                notification.message_content
            )
            
            if result['success']:
                notification.status = 'sent'
                notification.sent_at = timezone.now()
                notification.delivery_status = result.get('status', '')
            else:
                notification.status = 'failed'
            
            notification.save()
            
        except Exception as e:
            print(f"Error sending notification {notification.id}: {e}")

@shared_task
def send_daily_risk_alerts():
    """Send daily alerts for high-risk students"""
    from apps.students.models import Student
    
    high_risk_students = Student.objects.filter(current_risk_level='high')
    sms_service = SMSService()
    
    for student in high_risk_students:
        # Check if alert was already sent today
        today = timezone.now().date()
        today_notifications = Notification.objects.filter(
            student=student,
            template__template_type='risk_alert',
            created_at__date=today
        )
        
        if not today_notifications.exists():
            sms_service.send_risk_alert(student, 'high')

@shared_task
def send_attendance_alerts():
    """Send alerts for students with poor attendance"""
    from apps.students.models import Student
    from apps.analytics.models import StudentAnalytics
    
    students_with_poor_attendance = StudentAnalytics.objects.filter(
        overall_attendance_percentage__lt=75
    ).select_related('student')
    
    sms_service = SMSService()
    
    for analytics in students_with_poor_attendance:
        # Send attendance warning
        try:
            template = NotificationTemplate.objects.get(
                template_type='attendance_warning',
                is_active=True
            )
            
            message = template.message_template.format(
                student_name=analytics.student.user.get_full_name(),
                attendance_percentage=analytics.overall_attendance_percentage,
                school_name="Your School Name"
            )
            
            Notification.objects.create(
                student=analytics.student,
                template=template,
                recipient_phone=analytics.student.parent_phone,
                message_content=message,
                status='pending'
            )
            
        except Exception as e:
            print(f"Error creating attendance notification: {e}")