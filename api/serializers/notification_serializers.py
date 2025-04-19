from rest_framework import serializers
from notifications.models import Notification, NotificationType

class NotificationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationType
        fields = ['id', 'name', 'description']

class NotificationSerializer(serializers.ModelSerializer):
    notification_type = NotificationTypeSerializer(read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'notification_type', 'title', 'message',
            'link', 'created_at', 'read', 'read_at'
        ]
        read_only_fields = ['created_at', 'read_at']