from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Avg, Count

from .models import SupplierProfile, SupplierDocument, SupplierRating, SupplierCategory
from .forms import SupplierProfileForm, SupplierDocumentForm, SupplierRatingForm
from accounts.decorators import supplier_required, buyer_required

@login_required
@buyer_required
def supplier_list(request):
    """List all verified suppliers"""
    # Get filter parameters
    category_id = request.GET.get('category')
    rating_min = request.GET.get('rating_min')
    search_query = request.GET.get('search')
    
    # Base queryset - only verified suppliers
    suppliers = SupplierProfile.objects.filter(is_verified=True)
    
    # Apply filters
    if category_id:
        suppliers = suppliers.filter(categories__id=category_id)
    
    if search_query:
        suppliers = suppliers.filter(
            company_name__icontains=search_query
        )
    
    # Annotate with average rating
    suppliers = suppliers.annotate(avg_rating=Avg('ratings__rating'))
    
    if rating_min:
        suppliers = suppliers.filter(avg_rating__gte=rating_min)
    
    # Get categories for filter sidebar
    categories = SupplierCategory.objects.all()
    
    return render(request, 'suppliers/supplier_list.html', {
        'suppliers': suppliers,
        'categories': categories,
        'current_category': category_id,
        'current_rating_min': rating_min,
        'current_search': search_query
    })

@login_required
def supplier_detail(request, pk):
    """View a supplier's profile"""
    supplier = get_object_or_404(SupplierProfile, pk=pk)
    
    # Check if user has permission to view this supplier
    is_owner = request.user == supplier.user
    is_buyer = hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'buyer'
    is_admin = request.user.is_staff
    
    if not (is_owner or is_buyer or is_admin):
        return HttpResponseForbidden("You don't have permission to view this supplier profile.")
    
    # Get supplier documents
    documents = supplier.documents.all()
    
    # Get ratings and calculate average
    ratings = supplier.ratings.all()
    avg_rating = ratings.aggregate(Avg('rating'))['rating__avg'] or 0
    rating_count = ratings.count()
    
    # Rating form for buyers
    rating_form = None
    user_rating = None
    
    if is_buyer:
        user_rating = ratings.filter(rated_by=request.user).first()
        
        if request.method == 'POST' and 'submit_rating' in request.POST:
            if user_rating:
                rating_form = SupplierRatingForm(request.POST, instance=user_rating)
            else:
                rating_form = SupplierRatingForm(request.POST)
                
            if rating_form.is_valid():
                rating = rating_form.save(commit=False)
                rating.supplier = supplier
                rating.rated_by = request.user
                rating.save()
                messages.success(request, "Rating submitted successfully.")
                return redirect('supplier_detail', pk=pk)
        else:
            rating_form = SupplierRatingForm(instance=user_rating)
    
    # Document upload form for supplier owner
    document_form = None
    if is_owner:
        if request.method == 'POST' and 'upload_document' in request.POST:
            document_form = SupplierDocumentForm(request.POST, request.FILES)
            if document_form.is_valid():
                document = document_form.save(commit=False)
                document.supplier = supplier
                document.save()
                messages.success(request, "Document uploaded successfully.")
                return redirect('supplier_detail', pk=pk)
        else:
            document_form = SupplierDocumentForm()
    
    return render(request, 'suppliers/supplier_detail.html', {
        'supplier': supplier,
        'documents': documents,
        'ratings': ratings,
        'avg_rating': avg_rating,
        'rating_count': rating_count,
        'is_owner': is_owner,
        'rating_form': rating_form,
        'document_form': document_form,
        'user_rating': user_rating
    })

@login_required
@supplier_required
def supplier_profile_edit(request):
    """Edit the supplier's own profile"""
    supplier = get_object_or_404(SupplierProfile, user=request.user)
    
    if request.method == 'POST':
        form = SupplierProfileForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('suppliers:supplier_detail', pk=supplier.pk)
    else:
        form = SupplierProfileForm(instance=supplier)
    
    return render(request, 'suppliers/supplier_profile_form.html', {
        'form': form,
        'supplier': supplier
    })

@login_required
@buyer_required
def supplier_rating(request, pk):
    """Rate a supplier"""
    supplier = get_object_or_404(SupplierProfile, pk=pk)
    user_rating = SupplierRating.objects.filter(supplier=supplier, rated_by=request.user).first()
    
    if request.method == 'POST':
        if user_rating:
            form = SupplierRatingForm(request.POST, instance=user_rating)
        else:
            form = SupplierRatingForm(request.POST)
            
        if form.is_valid():
            rating = form.save(commit=False)
            rating.supplier = supplier
            rating.rated_by = request.user
            rating.save()
            messages.success(request, "Rating submitted successfully.")
            return redirect('supplier_detail', pk=pk)
    else:
        form = SupplierRatingForm(instance=user_rating)
    
    return render(request, 'suppliers/supplier_rating_form.html', {
        'form': form,
        'supplier': supplier,
        'user_rating': user_rating
    })

@login_required
@supplier_required
def supplier_document_delete(request, pk):
    """Delete a supplier document"""
    document = get_object_or_404(SupplierDocument, pk=pk)
    supplier = document.supplier
    
    # Ensure user owns this document
    if supplier.user != request.user:
        return HttpResponseForbidden("You don't have permission to delete this document.")
    
    if request.method == 'POST':
        document.delete()
        messages.success(request, "Document deleted successfully.")
        return redirect('supplier_detail', pk=supplier.pk)
    
    return render(request, 'suppliers/supplier_document_confirm_delete.html', {
        'document': document
    })