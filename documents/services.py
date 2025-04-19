from django.core.files import File
from .models import Document, DocumentCategory
import os
import tempfile

def process_document(file_obj, title, category_name, description, uploaded_by, visibility='private'):
    """
    Process a document file and create a Document instance
    
    Args:
        file_obj: Django file object or path to file
        title: Document title
        category_name: Category name (will be created if doesn't exist)
        description: Document description
        uploaded_by: User who is uploading the document
        visibility: Document visibility (public, private, restricted)
    
    Returns:
        Document instance
    """
    # Get or create category
    category, created = DocumentCategory.objects.get_or_create(
        name=category_name,
        defaults={'description': f'Category for {category_name}'}
    )
    
    # Create document
    document = Document(
        title=title,
        category=category,
        description=description,
        uploaded_by=uploaded_by,
        visibility=visibility
    )
    
    # Handle file object or path
    if isinstance(file_obj, str) and os.path.exists(file_obj):
        with open(file_obj, 'rb') as f:
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            temp_file.write(f.read())
            temp_file.close()
            
            with open(temp_file.name, 'rb') as f:
                document.file.save(os.path.basename(file_obj), File(f))
            
            os.unlink(temp_file.name)
    else:
        # Assume it's a Django file object
        document.file = file_obj
        document.save()
    
    return document