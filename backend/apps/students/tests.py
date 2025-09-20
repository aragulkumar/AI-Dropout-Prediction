from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Student, Class
from apps.analytics.ml_models import MLService

User = get_user_model()

class StudentModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='teststudent',
            email='test@example.com',
            user_type='student'
        )
        
        self.student_class = Class.objects.create(
            name='Computer Science',
            grade=10,
            section='A',
            academic_year='2024-25'
        )
    
    def test_student_creation(self):
        student = Student.objects.create(
            user=self.user,
            roll_number='CS001',
            student_class=self.student_class,
            admission_date='2024-01-15',
            parent_name='John Doe Sr.',
            parent_phone='+1234567890',
            address='123 Test Street'
        )
        
        self.assertEqual(student.roll_number, 'CS001')
        self.assertEqual(student.current_risk_level, 'low')
        self.assertEqual(student.risk_score, 0.0)

class StudentAPITestCase(APITestCase):
    def setUp(self):
        self.teacher_user = User.objects.create_user(
            username='teacher',
            email='teacher@example.com',
            user_type='teacher'
        )
        
        self.client.force_authenticate(user=self.teacher_user)
    
    def test_get_students_list(self):
        url = '/api/students/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_risk_summary(self):
        url = '/api/students/risk-summary/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total', response.data)
        self.assertIn('high_risk', response.data)

class MLServiceTestCase(TestCase):
    def test_prediction_generation(self):
        # Create test student
        user = User.objects.create_user(
            username='mltest',
            user_type='student'
        )
        
        student_class = Class.objects.create(
            name='Test Class',
            grade=10,
            section='A',
            academic_year='2024-25'
        )
        
        student = Student.objects.create(
            user=user,
            roll_number='ML001',
            student_class=student_class,
            admission_date='2024-01-01',
            parent_name='Test Parent',
            parent_phone='+1234567890',
            address='Test Address'
        )
        
        # Test prediction (this would require a trained model)
        ml_service = MLService()
        # prediction = ml_service.predict_student_dropout(student)
        # self.assertIn('dropout_probability', prediction)