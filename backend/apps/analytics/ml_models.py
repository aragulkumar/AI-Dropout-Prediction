import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
import os
from django.conf import settings

class DropoutPredictor:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_columns = [
            'attendance_percentage',
            'gpa',
            'consecutive_absences',
            'failing_subjects',
            'late_submissions',
            'fee_overdue_days',
            'age',
            'parent_education_level',
            'family_income_bracket'
        ]
    
    def prepare_features(self, student_data):
        """Prepare features for prediction"""
        features = []
        
        for student in student_data:
            feature_row = [
                student.get('attendance_percentage', 0),
                student.get('gpa', 0),
                student.get('consecutive_absences', 0),
                student.get('failing_subjects', 0),
                student.get('late_submissions', 0),
                student.get('fee_overdue_days', 0),
                student.get('age', 18),
                student.get('parent_education_level', 1),  # Encoded values
                student.get('family_income_bracket', 2)
            ]
            features.append(feature_row)
        
        return pd.DataFrame(features, columns=self.feature_columns)
    
    def train_model(self, training_data, labels):
        """Train the dropout prediction model"""
        # Prepare features
        X = self.prepare_features(training_data)
        y = np.array(labels)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train multiple models and select best
        models = {
            'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'gradient_boosting': GradientBoostingClassifier(n_estimators=100, random_state=42)
        }
        
        best_model = None
        best_score = 0
        
        for name, model in models.items():
            # Cross-validation
            cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5)
            avg_score = cv_scores.mean()
            
            if avg_score > best_score:
                best_score = avg_score
                best_model = model
        
        # Train best model
        best_model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = best_model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        
        self.model = best_model
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'cross_val_score': best_score
        }
    
    def predict_dropout_probability(self, student_features):
        """Predict dropout probability for a student"""
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        # Prepare features
        X = self.prepare_features([student_features])
        X_scaled = self.scaler.transform(X)
        
        # Get probability
        probability = self.model.predict_proba(X_scaled)[0][1]  # Probability of dropout
        
        # Get feature importance for explanation
        feature_importance = dict(zip(
            self.feature_columns,
            self.model.feature_importances_
        ))
        
        return {
            'dropout_probability': probability,
            'risk_level': self._get_risk_level(probability),
            'feature_importance': feature_importance
        }
    
    def _get_risk_level(self, probability):
        """Convert probability to risk level"""
        if probability >= 0.7:
            return 'high'
        elif probability >= 0.4:
            return 'medium'
        else:
            return 'low'
    
    def save_model(self, model_name):
        """Save trained model to disk"""
        model_dir = os.path.join(settings.BASE_DIR, 'ml_models')
        os.makedirs(model_dir, exist_ok=True)
        
        model_path = os.path.join(model_dir, f'{model_name}.pkl')
        scaler_path = os.path.join(model_dir, f'{model_name}_scaler.pkl')
        
        joblib.dump(self.model, model_path)
        joblib.dump(self.scaler, scaler_path)
        
        return model_path
    
    def load_model(self, model_path):
        """Load trained model from disk"""
        scaler_path = model_path.replace('.pkl', '_scaler.pkl')
        
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)

# ML Service Class
class MLService:
    def __init__(self):
        self.predictor = DropoutPredictor()
        self._load_active_model()
    
    def _load_active_model(self):
        """Load the active ML model"""
        from .models import PredictionModel
        
        try:
            active_model = PredictionModel.objects.filter(is_active=True).first()
            if active_model:
                self.predictor.load_model(active_model.model_file_path)
        except Exception as e:
            print(f"Error loading model: {e}")
    
    def predict_student_dropout(self, student):
        """Predict dropout risk for a single student"""
        from .models import StudentAnalytics
        
        try:
            analytics = StudentAnalytics.objects.get(student=student)
            
            student_features = {
                'attendance_percentage': analytics.overall_attendance_percentage,
                'gpa': analytics.overall_gpa,
                'consecutive_absences': analytics.consecutive_absences,
                'failing_subjects': analytics.failing_subjects_count,
                'late_submissions': analytics.late_submissions,
                'fee_overdue_days': analytics.overdue_payments,
                'age': self._calculate_age(student.user.profile.date_of_birth),
                'parent_education_level': 2,  # Default value
                'family_income_bracket': 2   # Default value
            }
            
            prediction = self.predictor.predict_dropout_probability(student_features)
            
            # Save prediction to database
            self._save_prediction(student, prediction)
            
            return prediction
            
        except Exception as e:
            print(f"Error predicting dropout for student {student.roll_number}: {e}")
            return {'dropout_probability': 0, 'risk_level': 'low'}
    
    def _calculate_age(self, birth_date):
        """Calculate age from birth date"""
        from datetime import date
        if birth_date:
            today = date.today()
            return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return 18  # Default age
    
    def _save_prediction(self, student, prediction):
        """Save prediction to database"""
        from .models import DropoutPrediction, PredictionModel
        
        active_model = PredictionModel.objects.filter(is_active=True).first()
        if active_model:
            DropoutPrediction.objects.create(
                student=student,
                model=active_model,
                dropout_probability=prediction['dropout_probability'],
                risk_factors=prediction.get('feature_importance', {}),
                confidence_score=0.85  # Default confidence
            )