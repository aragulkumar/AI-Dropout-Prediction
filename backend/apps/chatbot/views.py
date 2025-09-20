from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import ChatSession, ChatMessage
from .serializers import ChatMessageSerializer, ChatSessionSerializer
from .chatbot_service import ChatbotService

class ChatSessionListView(generics.ListAPIView):
    serializer_class = ChatSessionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user)

class ChatMessageListView(generics.ListAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        session_id = self.kwargs['session_id']
        return ChatMessage.objects.filter(
            session__session_id=session_id,
            session__user=self.request.user
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message_view(request):
    """Send message to chatbot and get response"""
    try:
        user_message = request.data.get('message', '').strip()
        
        if not user_message:
            return Response(
                {'error': 'Message cannot be empty'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        chatbot_service = ChatbotService()
        session = chatbot_service.get_or_create_session(request.user)
        
        bot_response = chatbot_service.generate_response(user_message, session)
        
        return Response({
            'session_id': session.session_id,
            'user_message': user_message,
            'bot_response': bot_response,
            'timestamp': timezone.now()
        })
        
    except Exception as e:
        return Response(
            {'error': 'Failed to process message'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def end_session_view(request, session_id):
    """End a chat session"""
    try:
        session = ChatSession.objects.get(
            session_id=session_id,
            user=request.user
        )
        
        session.is_active = False
        session.ended_at = timezone.now()
        session.save()
        
        return Response({'message': 'Session ended successfully'})
        
    except ChatSession.DoesNotExist:
        return Response(
            {'error': 'Session not found'},
            status=status.HTTP_404_NOT_FOUND
        )