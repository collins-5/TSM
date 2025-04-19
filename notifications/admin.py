from django.contrib import admin
from .models import Notification, NotificationType

@admin.register(NotificationType)
class NotificationTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'recipient', 'notification_type', 'created_at', 'read')
    list_filter = ('read', 'notification_type', 'created_at')
    search_fields = ('title', 'message', 'recipient__username')
    date_hierarchy = 'created_at'