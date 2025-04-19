from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
    """Custom user model that extends Django's AbstractUser"""
    
    USER_TYPE_CHOICES = (
        ('buyer', 'Buyer'),
        ('supplier', 'Supplier'),
        ('admin', 'Administrator'),
    )
    
    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='buyer',
        verbose_name=_('User Type')
    )
    company_name = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(_('email address'), unique=True)
    
    # Use email as the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'user_type']
    
    @property
    def is_buyer(self):
        return self.user_type == 'buyer'
    
    @property
    def is_supplier(self):
        return self.user_type == 'supplier'
    
    @property
    def is_admin_user(self):
        return self.user_type == 'admin'
    
    class Meta:
        permissions = [
            ("manage_buyers", "Can manage buyer accounts"),
            ("manage_suppliers", "Can manage supplier accounts"),
        ]
        
    def __str__(self):
        return f"{self.email} ({self.get_user_type_display()})"


class UserProfile(models.Model):
    """Extended profile information for users"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    tax_id = models.CharField(max_length=50, blank=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)
    
    # Supplier-specific fields
    business_category = models.CharField(max_length=100, blank=True)
    years_in_business = models.PositiveIntegerField(default=0)
    
    # Buyer-specific fields
    department = models.CharField(max_length=100, blank=True)
    position = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


