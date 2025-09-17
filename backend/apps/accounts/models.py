from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('admin', 'Super Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    ]
    
    user_type = models.CharField(
        max_length=20, 
        choices=USER_TYPE_CHOICES,
        default='student'
    )
    phone = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to='profiles/', 
        blank=True, 
        null=True
    )
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True)
    
    # Contact information
    emergency_contact = models.CharField(max_length=15, blank=True, null=True)
    parent_phone = models.CharField(max_length=15, blank=True, null=True)
    parent_email = models.EmailField(blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'auth_user'
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()