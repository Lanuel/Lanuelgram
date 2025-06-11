from django.db import models
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from cloudinary.models import CloudinaryField
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class ProfileReactivationError(Exception):
    """Custom exception for profile reactivation errors"""
    pass

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = CloudinaryField('avatar', folder="Lanuelgram/", null=True, blank=True)
    displayname = models.CharField(max_length=30, null=True, blank=True)
    info = models.TextField(null=True, blank=True) 
    email = models.EmailField(null=True)
    location = models.CharField(max_length=40, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True,null=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)
    
    # Class constants
    REACTIVATION_GRACE_PERIOD_DAYS = 30
    
    def deactivate(self):
        """Deactivate the user account and record timestamp"""
        if not self.user.is_active:
            logger.warning(f"Attempted to deactivate already inactive user {self.user.id}")
            return  # Already deactivated
            
        self.user.is_active = False
        self.deactivated_at = timezone.now()
        
        # Save both models
        self.user.save(update_fields=['is_active'])
        self.save(update_fields=['deactivated_at'])
        
        logger.info(f"User {self.user.username} (ID: {self.user.id}) account deactivated")
    
    def can_reactivate(self):
        """Check if account can be reactivated (within grace period)"""
        if not self.deactivated_at:
            return False  # Was never properly deactivated
            
        grace_period_end = self.deactivated_at + timedelta(days=self.REACTIVATION_GRACE_PERIOD_DAYS)
        return timezone.now() <= grace_period_end
    
    def days_until_permanent_deactivation(self):
        """Get number of days left until permanent deactivation"""
        if not self.deactivated_at:
            return None
            
        grace_period_end = self.deactivated_at + timedelta(days=self.REACTIVATION_GRACE_PERIOD_DAYS)
        remaining = grace_period_end - timezone.now()
        
        if remaining.total_seconds() <= 0:
            return 0
            
        return remaining.days + 1  # Add 1 to include partial days
    
    def reactivate(self):
        """Reactivate the user account if within grace period."""
        # Check if user is already active
        if self.user.is_active:
            logger.warning(f"Attempted to reactivate already active user {self.user.id}")
            return  # Already active
        
        # Check if account was properly deactivated
        if not self.deactivated_at:
            raise ProfileReactivationError(
                "Account cannot be reactivated - no deactivation record found."
            )
        
        # Check grace period
        if not self.can_reactivate():
            days_past = (timezone.now() - self.deactivated_at).days
            raise ProfileReactivationError(
                f"Account cannot be reactivated after {self.REACTIVATION_GRACE_PERIOD_DAYS} days. "
                f"This account was deactivated {days_past} days ago."
            )
        
        # Reactivate the account
        self.user.is_active = True
        self.deactivated_at = None
        
        self.user.save(update_fields=['is_active'])
        self.save(update_fields=['deactivated_at'])
        
        logger.info(f"User {self.user.username} (ID: {self.user.id}) account reactivated")
    
    @property
    def is_deactivated(self):
        """Check if profile is deactivated"""
        return not self.user.is_active and self.deactivated_at is not None
    
    @property
    def is_permanently_deactivated(self):
        """Check if profile is permanently deactivated (past grace period)"""
        return self.is_deactivated and not self.can_reactivate()
    
    def __str__(self):
        return str(self.user)
    

    @property
    def name(self):
        if self.displayname:
            return self.displayname
        return self.user.username 
    
    @property
    def avatar(self):
        if self.image:
            return self.image.url
        return f'{settings.STATIC_URL}images/avatar.svg'
