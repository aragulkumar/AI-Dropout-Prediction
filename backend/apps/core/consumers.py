import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

User = get_user_model()

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        
        if self.user.is_authenticated:
            self.room_group_name = f"notifications_{self.user.id}"
            
            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            await self.accept()
        else:
            await self.close()
    
    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'ping':
            await self.send(text_data=json.dumps({
                'type': 'pong',
                'timestamp': str(timezone.now())
            }))
    
    async def send_notification(self, event):
        """Send notification to user"""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': event['notification']
        }))

class DashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        
        if self.user.is_authenticated and self.user.user_type in ['teacher', 'admin']:
            self.room_group_name = "dashboard_updates"
            
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            await self.accept()
        else:
            await self.close()
    
    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
    
    async def dashboard_update(self, event):
        """Send dashboard update"""
        await self.send(text_data=json.dumps({
            'type': 'dashboard_update',
            'data': event['data']
        }))

# Signal handlers for real-time updates
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@receiver(post_save, sender='students.Student')
def student_updated(sender, instance, created, **kwargs):
    """Send real-time update when student is updated"""
    channel_layer = get_channel_layer()
    
    # Send to dashboard
    async_to_sync(channel_layer.group_send)(
        "dashboard_updates",
        {
            "type": "dashboard_update",
            "data": {
                "action": "created" if created else "updated",
                "student_id": instance.id,
                "risk_level": instance.current_risk_level
            }
        }
    )
    
    # Send notification to student if risk level changed
    if not created and instance.current_risk_level == 'high':
        async_to_sync(channel_layer.group_send)(
            f"notifications_{instance.user.id}",
            {
                "type": "send_notification",
                "notification": {
                    "title": "Risk Alert",
                    "message": "Your academic risk level has been updated. Please contact your counselor.",
                    "type": "warning"
                }
            }
        )