from django.db import models
from django.conf import settings
import os
import uuid

def document_file_path(instance, filename):
    """Generate file path for new document"""
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    
    return os.path.join('uploads/documents/', filename)

class DocumentCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Document categories"

class Document(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to=document_file_path)
    category = models.ForeignKey(
        DocumentCategory, 
        on_delete=models.CASCADE,
        related_name='documents'
    )
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploaded_documents'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Document visibility
    PUBLIC = 'public'
    PRIVATE = 'private'
    RESTRICTED = 'restricted'
    
    VISIBILITY_CHOICES = [
        (PUBLIC, 'Public'),
        (PRIVATE, 'Private'),
        (RESTRICTED, 'Restricted')
    ]
    
    visibility = models.CharField(
        max_length=10,
        choices=VISIBILITY_CHOICES,
        default=PRIVATE
    )
    
    # If visibility is restricted, these users can access the document
    authorized_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='accessible_documents',
        blank=True
    )
    
    def __str__(self):
        return self.title
    
    def filename(self):
        return os.path.basename(self.file.name)
    
    def file_extension(self):
        name, extension = os.path.splitext(self.file.name)
        return extension
    
    def file_size(self):
        if self.file and hasattr(self.file, 'size'):
            return self.file.size
        return 0
    
    def can_access(self, user):
        if self.visibility == self.PUBLIC:
            return True
        
        if user == self.uploaded_by:
            return True
        
        if self.visibility == self.RESTRICTED and user in self.authorized_users.all():
            return True
        
        return False