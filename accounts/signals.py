# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserProfile
from suppliers.models import SupplierProfile

User = get_user_model()

@receiver(post_save, sender=User)
def create_or_update_profiles(sender, instance, created, **kwargs):
    """Signal to create or update UserProfile and SupplierProfile based on user type."""
    try:
        UserProfile.objects.get_or_create(user=instance)
    except Exception as e:
        print(f"Error creating/updating UserProfile: {e}")

    if instance.user_type == 'supplier':
        try:
            SupplierProfile.objects.get_or_create(user=instance)
        except Exception as e:
            print(f"Error creating/updating SupplierProfile: {e}")

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Signal to save UserProfile when a User is saved."""
    try:
        instance.profile.save()
    except AttributeError:
        # Handle the case where instance.profile might not exist yet
        pass

@receiver(post_save, sender=User)
def save_supplier_profile(sender, instance, **kwargs):
    """Signal to save SupplierProfile when a User is saved (if user is a supplier)."""
    if instance.user_type == 'supplier':
        try:
            instance.supplier_profile.save()
        except AttributeError:
            # Handle the case where instance.supplier_profile might not exist yet
            pass