# tenders/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Tender, TenderCategory, TenderDocument
from .forms import TenderForm, TenderDocumentForm, TenderSearchForm
from accounts.decorators import buyer_required

def tender_list(request):
    form = TenderSearchForm(request.GET)
    tenders = Tender.objects.all()
    
    if form.is_valid():
        query = form.cleaned_data.get('query')
        category = form.cleaned_data.get('category')
        is_active = form.cleaned_data.get('is_active')
        
        if query:
            tenders = tenders.filter(
                Q(title__icontains=query) | 
                Q(description__icontains=query) |
                Q(reference_number__icontains=query)
            )
        
        if category:
            tenders = tenders.filter(categories=category)
        
        if is_active:
            tenders = tenders.filter(is_active=True)
    
    context = {
        'tenders': tenders,
        'form': form,
    }
    return render(request, 'tenders/tender_list.html', context)

@buyer_required
def tender_create(request):
    if request.method == 'POST':
        form = TenderForm(request.POST)
        if form.is_valid():
            tender = form.save(commit=False)
            tender.created_by = request.user
            tender.save()
            form.save_m2m()  # Save many-to-many fields
            messages.success(request, 'Tender created successfully!')
            return redirect('tenders:tender_detail', pk=tender.pk)
    else:
        form = TenderForm()
    
    return render(request, 'tenders/tender_form.html', {'form': form})

def tender_detail(request, pk):
    tender = get_object_or_404(Tender, pk=pk)
    
    # Check if the user has permission to view the tender details
    is_owner = request.user == tender.created_by
    
    context = {
        'tender': tender,
        'is_owner': is_owner,
        'documents': tender.documents.filter(is_public=True) if not is_owner else tender.documents.all(),
    }
    
    # If the user is a supplier, check if they've already bid
    if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'supplier':
        from bidding.models import Bid
        context['has_bid'] = Bid.objects.filter(tender=tender, supplier=request.user).exists()
    
    return render(request, 'tenders/tender_detail.html', context)

@buyer_required
def tender_update(request, pk):
    tender = get_object_or_404(Tender, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        form = TenderForm(request.POST, instance=tender)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tender updated successfully!')
            return redirect('tenders:tender_detail', pk=tender.pk)
    else:
        form = TenderForm(instance=tender)
    
    return render(request, 'tenders/tender_form.html', {'form': form, 'tender': tender})

@buyer_required
def tender_add_document(request, pk):
    tender = get_object_or_404(Tender, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        form = TenderDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.tender = tender
            document.save()
            messages.success(request, 'Document added successfully!')
            return redirect('tenders:tender_detail', pk=tender.pk)
    else:
        form = TenderDocumentForm()
    
    context = {
        'form': form,
        'tender': tender,
    }
    return render(request, 'tenders/document_form.html', context)

def category_list(request):
    categories = TenderCategory.objects.all()
    return render(request, 'tenders/category_list.html', {'categories': categories})
@buyer_required
def tender_close(request, pk):
    tender = get_object_or_404(Tender, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        tender.is_active = False
        tender.save()
        messages.success(request, 'Tender closed successfully!')
        return redirect('tenders:tender_detail', pk=tender.pk)
    
    # If it's a GET request, show confirmation page
    return render(request, 'tenders/tender_close_confirm.html', {'tender': tender})