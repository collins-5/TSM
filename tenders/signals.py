# tenders/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Tender
from notifications.models import Notification, NotificationType

@receiver(post_save, sender=Tender)
def notify_on_tender_create(sender, instance, created, **kwargs):
    """
    Send notifications when a new tender is created or updated
    """
    if created:
        # Create notification type if it doesn't exist
        notification_type, _ = NotificationType.objects.get_or_create(
            name="new_tender",
            defaults={
                "description": "New tender has been published"
            }
        )
        tender_category_names = instance.categories.values_list('name', flat=True)
        # Try to get all suppliers that match the tender categories
        from suppliers.models import SupplierProfile
        matching_suppliers = SupplierProfile.objects.filter(
            categories__name__in=tender_category_names
        ).distinct()
        
        # Create notifications for matching suppliers
        for supplier in matching_suppliers:
            Notification.objects.create(
                recipient=supplier.user,
                notification_type=notification_type,
                title=f"New Tender: {instance.title}",
                message=f"A new tender has been published that matches your business categories.",
                related_object_id=instance.id
            )