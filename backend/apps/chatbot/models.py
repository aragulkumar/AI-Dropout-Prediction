from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=100, unique=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Chat session for {self.user.username}"

class ChatMessage(models.Model):
    MESSAGE_TYPES = [
        ('user', 'User'),
        ('bot', 'Bot'),
        ('system', 'System'),
    ]
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE)
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict)  # For storing additional data
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.message_type}: {self.content[:50]}..."

# Chatbot Service
import openai
from django.conf import settings

class ChatbotService:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.system_prompt = """
        You are an AI counselor for students in an educational institution. 
        Your role is to provide emotional support, academic guidance, and help 
        students with their concerns. Be empathetic, encouraging, and professional.
        
        Guidelines:
        - Listen actively to student concerns
        - Provide constructive advice
        - Encourage students to seek human help for serious issues
        - Be supportive and non-judgmental
        - Focus on academic and emotional wellbeing
        """
    
    def get_or_create_session(self, user):
        """Get or create active chat session for user"""
        import uuid
        
        active_session = ChatSession.objects.filter(
            user=user,
            is_active=True
        ).first()
        
        if not active_session:
            active_session = ChatSession.objects.create(
                user=user,
                session_id=str(uuid.uuid4())
            )
        
        return active_session
    
    def generate_response(self, user_message, session):
        """Generate AI response using OpenAI"""
        try:
            # Get conversation history
            messages = self._get_conversation_history(session)
            
            # Add system prompt
            full_messages = [
                {"role": "system", "content": self.system_prompt}
            ] + messages + [
                {"role": "user", "content": user_message}
            ]
            
            # Generate response
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=full_messages,
                max_tokens=500,
                temperature=0.7
            )
            
            bot_response = response.choices[0].message.content.strip()
            
            # Save messages
            ChatMessage.objects.create(
                session=session,
                message_type='user',
                content=user_message
            )
            
            ChatMessage.objects.create(
                session=session,
                message_type='bot',
                content=bot_response
            )
            
            # Check for crisis indicators
            self._check_crisis_indicators(user_message, session)
            
            return bot_response
            
        except Exception as e:
            return "I'm sorry, I'm having trouble responding right now. Please try again later."
    
    def _get_conversation_history(self, session):
        """Get recent conversation history"""
        recent_messages = ChatMessage.objects.filter(
            session=session
        ).order_by('-timestamp')[:10]
        
        messages = []
        for msg in reversed(recent_messages):
            role = "user" if msg.message_type == "user" else "assistant"
            messages.append({
                "role": role,
                "content": msg.content
            })
        
        return messages
    
    def _check_crisis_indicators(self, message, session):
        """Check for mental health crisis indicators"""
        crisis_keywords = [
            'suicide', 'kill myself', 'end my life', 'hurt myself',
            'self harm', 'hopeless', 'worthless', 'nobody cares'
        ]
        
        message_lower = message.lower()
        
        for keyword in crisis_keywords:
            if keyword in message_lower:
                # Create alert for counselors
                self._create_crisis_alert(session)
                break
    
    def _create_crisis_alert(self, session):
        """Create crisis alert for human intervention"""
        from apps.notifications.models import Notification, NotificationTemplate
        
        try:
            # Create system notification for counselors
            ChatMessage.objects.create(
                session=session,
                message_type='system',
                content="Crisis indicators detected. Human counselor alerted.",
                metadata={
                    'alert_type': 'crisis',
                    'severity': 'high',
                    'timestamp': timezone.now().isoformat()
                }
            )
            
            # Send notification to counselors (implementation depends on your setup)
            
        except Exception as e:
            print(f"Error creating crisis alert: {e}")