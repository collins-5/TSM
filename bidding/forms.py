from django import forms
from .models import Bid, BidDocument, BidEvaluation

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['amount', 'description', 'technical_details', 'delivery_timeline']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'technical_details': forms.Textarea(attrs={'rows': 6}),
        }

class BidDocumentForm(forms.ModelForm):
    class Meta:
        model = BidDocument
        fields = ['title', 'document']

class BidEvaluationForm(forms.ModelForm):
    class Meta:
        model = BidEvaluation
        fields = ['technical_score', 'financial_score', 'comments']
        widgets = {
            'comments': forms.Textarea(attrs={'rows': 4}),
        }