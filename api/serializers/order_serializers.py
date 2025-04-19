from rest_framework import serializers
from orders.models import Order, OrderItem, OrderStatus, Issue

class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatus
        fields = ['id', 'name', 'description']

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            'id', 'order', 'item_name', 'description', 'quantity',
            'unit_price', 'total_price'
        ]

class IssueSerializer(serializers.ModelSerializer):
    reported_by = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Issue
        fields = [
            'id', 'order', 'title', 'description', 'reported_by',
            'reported_at', 'resolved', 'resolved_at', 'resolution_notes'
        ]
        read_only_fields = ['reported_by', 'reported_at', 'resolved_at']

class OrderSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    status = serializers.PrimaryKeyRelatedField(queryset=OrderStatus.objects.all())
    
    class Meta:
        model = Order
        fields = [
            'id', 'contract', 'order_number', 'description', 'issued_date',
            'delivery_date', 'delivery_address', 'total_amount',
            'created_by', 'created_at', 'updated_at', 'status'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['status'] = OrderStatusSerializer(instance.status).data
        return representation