from django.db import models
from django.conf import settings
from tenders.models import Tender

class Bid(models.Model):
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name='bids')
    supplier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bids')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField()
    technical_details = models.TextField()
    delivery_timeline = models.IntegerField(help_text="Delivery time in days")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('under_review', 'Under Review'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    class Meta:
        unique_together = ('tender', 'supplier')
        ordering = ['amount']
    
    def __str__(self):
        return f"Bid for {self.tender.title} by {self.supplier.username}"

class BidDocument(models.Model):
    bid = models.ForeignKey(Bid, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255)
    document = models.FileField(upload_to='bid_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class BidEvaluation(models.Model):
    bid = models.OneToOneField(Bid, on_delete=models.CASCADE, related_name='evaluation')
    evaluator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='evaluations')
    technical_score = models.DecimalField(max_digits=5, decimal_places=2)
    financial_score = models.DecimalField(max_digits=5, decimal_places=2)
    comments = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def total_score(self):
        return self.technical_score + self.financial_score
    
    def __str__(self):
        return f"Evaluation for {self.bid}"