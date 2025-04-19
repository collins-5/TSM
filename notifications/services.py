from django.utils import timezone
from .models import Notification, NotificationType

def create_notification(recipient, notification_type_name, title, message, link=None):
    """
    Create a new notification
    
    Args:
        recipient: User object
        notification_type_name: String matching a NotificationType.name
        title: Notification title
        message: Notification message
        link: Optional link to include in the notification
    
    Returns:
        Newly created Notification object
    """
    notification_type, created = NotificationType.objects.get_or_create(
        name=notification_type_name,
        defaults={'description': f'Notification type for {notification_type_name}'}
    )
    
    notification = Notification.objects.create(
        recipient=recipient,
        notification_type=notification_type,
        title=title,
        message=message,
        link=link
    )
    
    return notification

def send_tender_notification(tender, notification_type_name, title, message):
    """
    Send notification to all suppliers about a tender
    """
    from accounts.models import UserProfile
    
    suppliers = UserProfile.objects.filter(user_type='supplier')
    
    for supplier in suppliers:
        create_notification(
            recipient=supplier.user,
            notification_type_name=notification_type_name,
            title=title,
            message=message,
            link=f'/tenders/{tender.id}/'
        )

def send_bid_notification(bid, notification_type_name, title, message):
    """
    Send notification to buyer about a bid
    """
    buyer = bid.tender.created_by
    
    create_notification(
        recipient=buyer,
        notification_type_name=notification_type_name,
        title=title,
        message=message,
        link=f'/bidding/bids/{bid.id}/'
    )