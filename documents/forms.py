from django import forms
from django.contrib.auth import get_user_model
from .models import Document, DocumentCategory

User = get_user_model()

class DocumentForm(forms.ModelForm):
    authorized_users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        help_text="Select users who can access this document if visibility is set to restricted."
    )
    
    class Meta:
        model = Document
        fields = ['title', 'file', 'category', 'description', 'visibility', 'authorized_users']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'visibility': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = DocumentCategory.objects.all()

class DocumentUpdateForm(DocumentForm):
    file = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        help_text="Leave empty to keep the current file."
    )
    
    class Meta(DocumentForm.Meta):
        pass
