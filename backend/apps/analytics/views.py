from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from .models import DropoutPrediction, StudentAnalytics
from .serializers import DropoutPredictionSerializer, StudentAnalyticsSerializer
from .ml_models import MLService

class StudentAnalyticsView(generics.RetrieveAPIView):
    queryset = StudentAnalytics.objects.all()
    serializer_class = StudentAnalyticsSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'student__roll_number'

class DropoutPredictionListView(generics.ListAPIView):
    serializer_class = DropoutPredictionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.user_type == 'student':
            # Students can only see their own predictions
            return DropoutPrediction.objects.filter(student__user=user)
        else:
            # Teachers and admins can see all predictions
            return DropoutPrediction.objects.all()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_prediction_view(request, roll_number):
    """Generate new prediction for a student"""
    try:
        from apps.students.models import Student
        
        student = Student.objects.get(roll_number=roll_number)
        ml_service = MLService()
        
        prediction = ml_service.predict_student_dropout(student)
        
        return Response({
            'student': roll_number,
            'prediction': prediction,
            'timestamp': timezone.now()
        })
        
    except Student.DoesNotExist:
        return Response(
            {'error': 'Student not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_analytics_view(request):
    """Get comprehensive analytics for dashboard"""
    from django.db.models import Count, Avg, Q
    from apps.students.models import Student, Attendance, Assessment
    
    # Overall statistics
    total_students = Student.objects.count()
    
    # Risk distribution
    risk_distribution = Student.objects.values('current_risk_level').annotate(
        count=Count('id')
    )
    
    # Attendance trends (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_attendance = Attendance.objects.filter(
        date__gte=thirty_days_ago
    ).values('date').annotate(
        present=Count('id', filter=Q(status='present')),
        absent=Count('id', filter=Q(status='absent'))
    ).order_by('date')
    
    # Academic performance trends
    performance_trends = Assessment.objects.filter(
        date_conducted__gte=thirty_days_ago
    ).values('subject__name').annotate(
        avg_percentage=Avg('obtained_marks')
    )
    
    return Response({
        'total_students': total_students,
        'risk_distribution': list(risk_distribution),
        'attendance_trends': list(recent_attendance),
        'performance_trends': list(performance_trends),
        'last_updated': timezone.now()
    })