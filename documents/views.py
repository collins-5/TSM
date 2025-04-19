from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.core.paginator import Paginator
from django.contrib import messages
from django.conf import settings
import os
import mimetypes

from .models import Document, DocumentCategory
from .forms import DocumentForm, DocumentUpdateForm

@login_required
def document_list(request):
    # Get all public documents + documents user has access to
    public_docs = Document.objects.filter(visibility=Document.PUBLIC)
    
    if request.user.is_authenticated:
        private_docs = Document.objects.filter(uploaded_by=request.user)
        restricted_docs = request.user.accessible_documents.all()
        
        # Combine querysets and remove duplicates
        documents = (public_docs | private_docs | restricted_docs).distinct()
    else:
        documents = public_docs
    
    # Add filter by category
    category_id = request.GET.get('category')
    if category_id:
        documents = documents.filter(category_id=category_id)
    
    # Add search functionality
    search_query = request.GET.get('search')
    if search_query:
        documents = documents.filter(title__icontains=search_query)
    
    categories = DocumentCategory.objects.all()
    
    # Pagination
    paginator = Paginator(documents, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'documents/document_list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'search_query': search_query,
        'category_id': category_id,
    })

@login_required
def document_upload(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.uploaded_by = request.user
            document.save()
            
            # If restricted visibility, add authorized users
            if document.visibility == Document.RESTRICTED and form.cleaned_data.get('authorized_users'):
                document.authorized_users.set(form.cleaned_data['authorized_users'])
            
            messages.success(request, f'Document "{document.title}" uploaded successfully.')
            return redirect('documents:document_detail', pk=document.id)
    else:
        form = DocumentForm()
    
    return render(request, 'documents/document_form.html', {
        'form': form,
        'action': 'Upload'
    })

@login_required
def document_detail(request, pk):
    document = get_object_or_404(Document, pk=pk)
    
    if not document.can_access(request.user):
        return HttpResponseForbidden("You don't have permission to view this document.")
    
    return render(request, 'documents/document_detail.html', {
        'document': document
    })

@login_required
def document_download(request, pk):
    document = get_object_or_404(Document, pk=pk)
    
    if not document.can_access(request.user):
        return HttpResponseForbidden("You don't have permission to download this document.")
    
    file_path = document.file.path
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type is None:
                mime_type = 'application/octet-stream'
            
            response = HttpResponse(fh.read(), content_type=mime_type)
            response['Content-Disposition'] = f'attachment; filename="{document.filename()}"'
            return response
    
    messages.error(request, "Document not found on the server.")
    return redirect('documents:document_list')

@login_required
def document_delete(request, pk):
    document = get_object_or_404(Document, pk=pk)
    
    # Only document owner can delete
    if request.user != document.uploaded_by and not request.user.is_staff:
        return HttpResponseForbidden("You don't have permission to delete this document.")
    
    if request.method == 'POST':
        document_title = document.title
        document.delete()
        messages.success(request, f'Document "{document_title}" deleted successfully.')
        return redirect('documents:document_list')
    
    return render(request, 'documents/document_confirm_delete.html', {
        'document': document
    })

@login_required
def document_update(request, pk):
    document = get_object_or_404(Document, pk=pk)
    
    # Only document owner can update
    if request.user != document.uploaded_by and not request.user.is_staff:
        return HttpResponseForbidden("You don't have permission to update this document.")
    
    if request.method == 'POST':
        form = DocumentUpdateForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            document = form.save()
            
            # Update authorized users if visibility is restricted
            if document.visibility == Document.RESTRICTED and form.cleaned_data.get('authorized_users'):
                document.authorized_users.set(form.cleaned_data['authorized_users'])
            
            messages.success(request, f'Document "{document.title}" updated successfully.')
            return redirect('documents:document_detail', pk=document.id)
    else:
        form = DocumentUpdateForm(instance=document)
    
    return render(request, 'documents/document_form.html', {
        'form': form,
        'action': 'Update',
        'document': document
    })