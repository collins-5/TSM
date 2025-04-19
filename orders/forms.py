from django import forms
from django.forms import inlineformset_factory

from .models import Order, OrderItem, Issue

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['delivery_address', 'delivery_date', 'special_instructions']
        widgets = {
            'delivery_date': forms.DateInput(attrs={'type': 'date'}),
            'special_instructions': forms.Textarea(attrs={'rows': 3}),
        }

# Create the formset for order items
OrderItemFormSet = inlineformset_factory(
    Order, 
    OrderItem,
    fields=('description', 'quantity', 'unit_price'),
    extra=1,
    can_delete=True
)

class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['title', 'description', 'priority']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class IssueUpdateForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['title', 'description', 'status', 'priority']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }