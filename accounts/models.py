from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class User(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=[
        ('read', 'Read'),
        ('write', 'Write'),
        ('admin', 'Admin')
    ], default='read')
    blocked_users = models.ManyToManyField('self', symmetrical=False, related_name='blocked_by')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def is_blocked(self, user):
        # Check if the given user is blocked by the current user
        return self.blocked_users.filter(id=user.id).exists()



class FriendRequest(models.Model):
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    BLOCKED = 'blocked'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
        (BLOCKED, 'Blocked')
    ]
    
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_requests')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('sender', 'receiver')
        indexes = [
            models.Index(fields=['sender', 'receiver', 'status']),
        ]

    def accept(self):
        self.status = self.ACCEPTED
        self.save()

    def reject(self):
        self.status = self.REJECTED
        self.save()

    def is_rejected_cooldown_active(self):
        cooldown_period = timedelta(hours=24)
        return self.status == self.REJECTED and self.updated_at + cooldown_period > timezone.now()
