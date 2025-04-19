from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Order, OrderItem, OrderStatus, Issue

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'contract', 'buyer', 'supplier', 'status', 'total_amount', 'delivery_date', 'created_at')
    list_filter = ('status', 'created_at', 'delivery_date')
    search_fields = ('order_number', 'buyer__username', 'supplier__username', 'contract__title')
    date_hierarchy = 'created_at'
    inlines = [OrderItemInline]

@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

class IssueAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'status', 'priority', 'raised_by', 'assigned_to', 'created_at')
    list_filter = ('status', 'priority', 'created_at')
    search_fields = ('title', 'description', 'order__order_number')
    date_hierarchy = 'created_at'

admin.site.register(Issue, IssueAdmin)