# tenders/forms.py
from django import forms
from .models import Tender, TenderDocument ,TenderCategory

class TenderForm(forms.ModelForm):
    class Meta:
        model = Tender
        fields = ['title', 'reference_number', 'description', 'requirements', 
                 'budget', 'submission_deadline', 'categories']
        widgets = {
            'submission_deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'requirements': forms.Textarea(attrs={'rows': 4}),
            'submission_deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }

class TenderDocumentForm(forms.ModelForm):
    class Meta:
        model = TenderDocument
        fields = ['title', 'file', 'is_public']

class TenderSearchForm(forms.Form):
    query = forms.CharField(required=False, label='Search', 
                           widget=forms.TextInput(attrs={'placeholder': 'Search tenders...'}))
    category = forms.ModelChoiceField(queryset=TenderCategory.objects.all(), 
                                     required=False, empty_label="All Categories")
    is_active = forms.BooleanField(required=False, initial=True, label='Active tenders only')