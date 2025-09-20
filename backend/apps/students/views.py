from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Avg, Count
from .models import Student, Attendance, Assessment, FeeRecord
from .serializers import StudentSerializer, AttendanceSerializer, AssessmentSerializer
from .permissions import IsTeacherOrAdmin

class StudentListView(generics.ListCreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['student_class', 'current_risk_level']
    search_fields = ['roll_number', 'user__first_name', 'user__last_name']
    ordering_fields = ['roll_number', 'risk_score', 'last_risk_update']

class StudentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'roll_number'

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def risk_summary_view(request):
    """Get risk level summary statistics"""
    summary = Student.objects.aggregate(
        total=Count('id'),
        high_risk=Count('id', filter=Q(current_risk_level='high')),
        medium_risk=Count('id', filter=Q(current_risk_level='medium')),
        low_risk=Count('id', filter=Q(current_risk_level='low'))
    )
    
    return Response(summary)

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def upload_data_view(request):
    """Handle bulk data upload (attendance, marks, fees)"""
    import pandas as pd
    from io import BytesIO
    
    try:
        file = request.FILES['file']
        data_type = request.data.get('dataType')
        
        # Read file
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.name.endswith('.xlsx'):
            df = pd.read_excel(file)
        else:
            return Response(
                {'error': 'Unsupported file format'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Process based on data type
        if data_type == 'attendance':
            process_attendance_data(df)
        elif data_type == 'marks':
            process_marks_data(df)
        elif data_type == 'fees':
            process_fees_data(df)
        else:
            return Response(
                {'error': 'Invalid data type'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({'message': 'Data uploaded successfully'})
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def process_attendance_data(df):
    """Process attendance data from uploaded file"""
    for _, row in df.iterrows():
        try:
            student = Student.objects.get(roll_number=row['roll_number'])
            # Process attendance logic
            # ... implementation details
        except Student.DoesNotExist:
            continue

def process_marks_data(df):
    """Process marks data from uploaded file"""
    # Similar implementation for marks
    pass

def process_fees_data(df):
    """Process fees data from uploaded file"""
    # Similar implementation for fees
    pass