# tenders/models.py
from django.db import models
from django.conf import settings
from django.urls import reverse

class TenderCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Tender Categories"

class TenderStage(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['order']

class Tender(models.Model):
    title = models.CharField(max_length=200)
    reference_number = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    requirements = models.TextField()
    budget = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submission_deadline = models.DateTimeField()
    
    # Status and categorization
    is_active = models.BooleanField(default=True)
    categories = models.ManyToManyField(TenderCategory, related_name='tenders')
    current_stage = models.ForeignKey(TenderStage, on_delete=models.SET_NULL, null=True, related_name='tenders')
    
    # Relations
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_tenders')
    
    def __str__(self):
        return f"{self.reference_number} - {self.title}"
    
    def get_absolute_url(self):
        return reverse('tenders:tender_detail', kwargs={'pk': self.pk})
    
    @property
    def is_deadline_passed(self):
        from django.utils import timezone
        return timezone.now() > self.submission_deadline

class TenderDocument(models.Model):
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='tender_documents/')
    is_public = models.BooleanField(default=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.tender.reference_number}"