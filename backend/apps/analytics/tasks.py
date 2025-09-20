from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Student, StudentAnalytics, DropoutPrediction
from .ml_models import MLService

@shared_task
def update_student_analytics():
    """Update analytics for all students"""
    students = Student.objects.all()
    ml_service = MLService()
    
    for student in students:
        try:
            # Update analytics
            analytics, created = StudentAnalytics.objects.get_or_create(student=student)
            
            # Calculate attendance percentage
            analytics.overall_attendance_percentage = calculate_attendance_percentage(student)
            
            # Calculate GPA
            analytics.overall_gpa = calculate_gpa(student)
            
            # Update other metrics
            analytics.consecutive_absences = calculate_consecutive_absences(student)
            analytics.failing_subjects_count = calculate_failing_subjects(student)
            
            analytics.save()
            
            # Generate dropout prediction
            ml_service.predict_student_dropout(student)
            
        except Exception as e:
            print(f"Error updating analytics for {student.roll_number}: {e}")

@shared_task
def retrain_ml_model():
    """Retrain the ML model with new data"""
    try:
        # Collect training data
        training_data, labels = collect_training_data()
        
        # Train model
        predictor = DropoutPredictor()
        metrics = predictor.train_model(training_data, labels)
        
        # Save new model if performance is good
        if metrics['accuracy'] > 0.75:
            model_path = predictor.save_model(f"dropout_model_{timezone.now().strftime('%Y%m%d_%H%M%S')}")
            
            # Create model record
            from .models import PredictionModel
            PredictionModel.objects.filter(is_active=True).update(is_active=False)
            
            PredictionModel.objects.create(
                name="Dropout Prediction Model",
                version=timezone.now().strftime('%Y%m%d_%H%M%S'),
                algorithm="Random Forest / Gradient Boosting",
                accuracy=metrics['accuracy'],
                is_active=True,
                model_file_path=model_path
            )
            
            print(f"New model trained with accuracy: {metrics['accuracy']:.4f}")
        
    except Exception as e:
        print(f"Error retraining model: {e}")

def calculate_attendance_percentage(student):
    """Calculate overall attendance percentage"""
    from django.db.models import Count, Q
    
    total_classes = student.attendance_set.count()
    if total_classes == 0:
        return 0
    
    present_classes = student.attendance_set.filter(
        Q(status='present') | Q(status='late')
    ).count()
    
    return (present_classes / total_classes) * 100

def calculate_gpa(student):
    """Calculate student's GPA"""
    from django.db.models import Avg
    
    avg_percentage = student.assessment_set.aggregate(
        avg_marks=Avg('obtained_marks')
    )['avg_marks']
    
    if avg_percentage is None:
        return 0
    
    # Convert percentage to GPA (4.0 scale)
    return min((avg_percentage / 100) * 4.0, 4.0)

def collect_training_data():
    """Collect historical data for model training"""
    # This would collect historical data of students who have dropped out
    # and those who have completed their education
    pass