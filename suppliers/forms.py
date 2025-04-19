from django import forms
from .models import SupplierProfile, SupplierDocument, SupplierRating

class SupplierProfileForm(forms.ModelForm):
    class Meta:
        model = SupplierProfile
        fields = [
            'company_name', 'registration_number', 'tax_id', 'company_address',
            'contact_person', 'contact_email', 'contact_phone', 'website',
            'year_established', 'categories', 'short_description', 'capabilities'
        ]
        widgets = {
            'company_address': forms.Textarea(attrs={'rows': 3}),
            'short_description': forms.Textarea(attrs={'rows': 3}),
            'capabilities': forms.Textarea(attrs={'rows': 5}),
            'categories': forms.CheckboxSelectMultiple()
        }

class SupplierDocumentForm(forms.ModelForm):
    class Meta:
        model = SupplierDocument
        fields = ['title', 'document', 'document_type']

class SupplierRatingForm(forms.ModelForm):
    class Meta:
        model = SupplierRating
        fields = ['rating', 'comments']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'comments': forms.Textarea(attrs={'rows': 4})
        }