from django.db import models
from django.utils import timezone
from django.conf import settings

from contracts.models import Contract

class OrderStatus(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Order Statuses"


class Order(models.Model):
    order_number = models.CharField(max_length=50, unique=True)
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='orders')
    
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='buyer_orders')
    supplier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='supplier_orders')
    status = models.ForeignKey(OrderStatus, on_delete=models.PROTECT)
    
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    delivery_address = models.TextField()
    delivery_date = models.DateField()
    special_instructions = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order {self.order_number}"
    
    class Meta:
        ordering = ['-created_at']

   


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    
    @property
    def total_price(self):
        return self.quantity * self.unit_price
    
    def __str__(self):
        return f"{self.description} ({self.quantity})"


class Issue(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    ISSUE_TYPE_CHOICES = [
        ('quality', 'Quality Issue'),
        ('delivery', 'Delivery Issue'),
        ('quantity', 'Quantity Issue'),
        ('payment', 'Payment Issue'),
        ('other', 'Other Issue'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='issues')
    title = models.CharField(max_length=255)
    description = models.TextField()
    
    issue_type = models.CharField(max_length=20, choices=ISSUE_TYPE_CHOICES)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='open')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    raised_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='raised_issues')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assigned_issues', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']