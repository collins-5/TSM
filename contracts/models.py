from django.db import models
from django.conf import settings
from tenders.models import Tender
from bidding.models import Bid


    # other fields...

class ContractStatus(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class Contract(models.Model):
   
    title = models.CharField(max_length=255)
    tender = models.OneToOneField(Tender, on_delete=models.CASCADE, related_name='contract', null=True, blank=True)
    winning_bid = models.OneToOneField(Bid, on_delete=models.CASCADE, related_name='contract', null=True, blank=True)
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='buyer_contracts')
    supplier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='supplier_contracts')
    status = models.ForeignKey(ContractStatus, on_delete=models.PROTECT, related_name='contracts')
    terms_and_conditions = models.TextField()
    scope_of_work = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    total_value = models.DecimalField(max_digits=15, decimal_places=2)
    payment_terms = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    termination_reason = models.TextField(blank=True, null=True)
    

    
    

    
    class Meta:
        ordering = ['-created_at']

class ContractDocument(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255)
    document = models.FileField(upload_to='contract_documents/')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    DOCUMENT_TYPES = (
        ('main', 'Main Contract'),
        ('amendment', 'Amendment'),
        ('attachment', 'Attachment'),
        ('invoice', 'Invoice'),
        ('payment', 'Payment Proof'),
        ('other', 'Other'),
    )
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    
    def __str__(self):
        return self.title

