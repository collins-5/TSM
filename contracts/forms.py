# contracts/forms.py
from django import forms
from .models import Contract, ContractDocument
from bidding.models import Bid

class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = [
            'title', 'terms_and_conditions', 'scope_of_work', 
            'start_date', 'end_date', 'total_value', 'payment_terms'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'terms_and_conditions': forms.Textarea(attrs={'rows': 5}),
            'scope_of_work': forms.Textarea(attrs={'rows': 5}),
            'payment_terms': forms.Textarea(attrs={'rows': 3}),
        }

class ContractFromBidForm(forms.Form):
    bid = forms.ModelChoiceField(
        queryset=Bid.objects.none(),
        widget=forms.Select(attrs={'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'})
    )
    
    def __init__(self, tender=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if tender:
            self.fields['bid'].queryset = Bid.objects.filter(tender=tender)

class ContractDocumentForm(forms.ModelForm):
    class Meta:
        model = ContractDocument
        fields = ['title', 'document', 'document_type']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'}),
            'document': forms.FileInput(attrs={'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'}),
            'document_type': forms.Select(attrs={'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'}),
        }