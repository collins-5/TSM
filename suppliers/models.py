from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class SupplierCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Supplier Categories"

class SupplierProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='supplier_profile')
    company_name = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=100)
    tax_id = models.CharField(max_length=100)
    company_address = models.TextField()
    contact_person = models.CharField(max_length=255)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    website = models.URLField(blank=True)
    year_established = models.PositiveIntegerField(null=True, blank=True)
    categories = models.ManyToManyField(SupplierCategory, related_name='suppliers')
    short_description = models.TextField()
    capabilities = models.TextField()
    is_verified = models.BooleanField(default=False)
    verified_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.company_name

class SupplierDocument(models.Model):
    supplier = models.ForeignKey(SupplierProfile, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255)
    document = models.FileField(upload_to='supplier_documents/')
    
    DOCUMENT_TYPES = (
        ('registration', 'Business Registration'),
        ('tax', 'Tax Certificate'),
        ('financial', 'Financial Statement'),
        ('certification', 'Quality Certification'),
        ('compliance', 'Compliance Certificate'),
        ('other', 'Other'),
    )
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class SupplierRating(models.Model):
    supplier = models.ForeignKey(SupplierProfile, on_delete=models.CASCADE, related_name='ratings')
    rated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='supplier_ratings')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comments = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('supplier', 'rated_by')
    
    def __str__(self):
        return f"{self.supplier.company_name} rated {self.rating}/5 by {self.rated_by.username}"