
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Max, Min
from django.http import HttpResponseForbidden

from contracts.models import Contract
from django.db.models import F, Count, Q, Avg, Sum

from suppliers.models import SupplierProfile

from .models import Bid, BidDocument, BidEvaluation
from .forms import BidForm, BidDocumentForm, BidEvaluationForm
from tenders.models import Tender
from accounts.decorators import supplier_required, buyer_required

@login_required
@supplier_required
def bid_create(request, tender_id):
    tender = get_object_or_404(Tender, pk=tender_id)
    user = request.user
    
    # Check if the tender is open for bidding
    if not tender.is_active:
        messages.error(request, "This tender is not open for bidding.")
        return redirect('tenders:tender_detail', pk=tender_id)
    
    # Check if the submission deadline has passed
    if tender.is_deadline_passed:
        messages.error(request, "The submission deadline for this tender has passed.")
        return redirect('tenders:tender_detail', pk=tender_id)
    
    # Check if supplier already placed a bid
    existing_bid = Bid.objects.filter(tender=tender, supplier=user).first()
    if existing_bid:
        messages.info(request, "You have already placed a bid for this tender. You can update it instead.")
        return redirect('bidding:bid_update', pk=existing_bid.pk)
    
    # Check if supplier has the required categories for this tender
    try:
        supplier_profile = user.supplier_profile
        supplier_categories = supplier_profile.categories.all()
        
        # Get tender categories
        tender_categories = tender.categories.all()
        
        # Check if there's at least one matching category by name
        supplier_category_names = supplier_categories.values_list('name', flat=True)
        tender_category_names = tender_categories.values_list('name', flat=True)
        
        has_matching_category = any(cat_name in tender_category_names for cat_name in supplier_category_names)
        
        if tender_categories.exists() and not has_matching_category:
            messages.warning(request, "Your supplier profile doesn't have any matching categories for this tender. You can still submit a bid, but it might be less likely to be accepted.")
    
    except SupplierProfile.DoesNotExist:
        messages.error(request, "You need to complete your supplier profile before bidding.")
        return redirect('suppliers:create_profile')
    
    if request.method == 'POST':
        form = BidForm(request.POST)
        if form.is_valid():
            bid = form.save(commit=False)
            bid.tender = tender
            bid.supplier = user
            bid.save()
            messages.success(request, "Your bid has been submitted successfully.")
            return redirect('bidding:bid_detail', pk=bid.pk)
    else:
        form = BidForm()
    
    return render(request, 'bidding/bid_form.html', {
        'form': form,
        'tender': tender,
        'is_create': True
    })

@login_required
def bid_update(request, pk):  # Changed from bid_id to pk
    bid = get_object_or_404(Bid, pk=pk)
    
    # Check if user is the owner of the bid
    if bid.supplier != request.user:
        messages.error(request, "You can only edit your own bids.")
        return redirect('bidding:bid_detail', bid_id=bid.id)
    
    # Check if the tender is still accepting bids
    if bid.tender.is_deadline_passed or not bid.tender.is_active:
        messages.error(request, "Bids can only be edited while the tender is open and before submission deadline.")
        return redirect('bidding:bid_detail', bid_id=bid.id)
    
    if request.method == 'POST':
        form = BidForm(request.POST, instance=bid)
        if form.is_valid():
            form.save()
            messages.success(request, "Your bid has been updated successfully.")
            return redirect('bidding:bid_detail', pk=bid.id)
    else:
        form = BidForm(instance=bid)
    
    return render(request, 'bidding/bid_form.html', {
        'form': form,
        'bid': bid,
        'tender': bid.tender,
        'is_create': False
    })

@login_required
def bid_list(request, tender_id):
    tender = get_object_or_404(Tender, pk=tender_id)
    
    # If user is not the tender owner, they can only see their own bid
    if request.user != tender.created_by:
        bid = get_object_or_404(Bid, tender=tender, supplier=request.user)
        return redirect('bidding:bid_detail', pk=bid.pk)
    
    bids = Bid.objects.filter(tender=tender)
    
    # Calculate bid statistics for the tender owner
    stats = {
        'count': bids.count(),
        'avg_amount': bids.aggregate(Avg('amount'))['amount__avg'],
        'min_amount': bids.aggregate(Min('amount'))['amount__min'],
        'max_amount': bids.aggregate(Max('amount'))['amount__max'],
    }
    
    # Check if a contract already exists for this tender
    has_contract = Contract.objects.filter(tender=tender).exists()
    
    return render(request, 'bidding/bid_list.html', {
        'tender': tender,
        'bids': bids,
        'stats': stats,
        'has_contract': has_contract
    })

@login_required
def bid_detail(request, pk):
    bid = get_object_or_404(Bid, pk=pk)
    
    # Check if user has permission to view this bid
    is_owner = bid.supplier == request.user
    is_tender_owner = bid.tender.created_by == request.user
    
    if not (is_owner or is_tender_owner):
        return HttpResponseForbidden("You don't have permission to view this bid.")
    
    # Check if this bid can be edited (for suppliers)
    can_edit = is_owner and not bid.tender.is_deadline_passed and bid.tender.is_active
    
    # Define can_award variable for tender owners
    can_award = is_tender_owner and not bid.tender.is_deadline_passed and bid.tender.is_active
    
    documents = bid.documents.all()
    
    # For tender owners, show evaluation form
    evaluation_form = None
    evaluation = BidEvaluation.objects.filter(bid=bid).first()
    
    if is_tender_owner:
        if request.method == 'POST' and 'evaluate' in request.POST:
            if evaluation:
                evaluation_form = BidEvaluationForm(request.POST, instance=evaluation)
            else:
                evaluation_form = BidEvaluationForm(request.POST)
                
            if evaluation_form.is_valid():
                eval_obj = evaluation_form.save(commit=False)
                eval_obj.bid = bid
                eval_obj.evaluator = request.user
                eval_obj.save()
                messages.success(request, "Bid evaluation saved successfully.")
                return redirect('bidding:bid_detail', pk=pk)
        else:
            evaluation_form = BidEvaluationForm(instance=evaluation)
    
    # For suppliers, show document upload form
    document_form = None
    if is_owner and bid.tender.is_active:  # Fixed comparison with boolean instead of string
        if request.method == 'POST' and 'upload' in request.POST:
            document_form = BidDocumentForm(request.POST, request.FILES)
            if document_form.is_valid():
                doc = document_form.save(commit=False)
                doc.bid = bid
                doc.save()
                messages.success(request, "Document uploaded successfully.")
                return redirect('bidding:bid_detail', pk=pk)
        else:
            document_form = BidDocumentForm()
    
    return render(request, 'bidding/bid_detail.html', {
        'bid': bid,
        'documents': documents,
        'is_owner': is_owner,
        'is_tender_owner': is_tender_owner,
        'can_edit': can_edit,
        'can_award': can_award,
        'evaluation': evaluation,
        'evaluation_form': evaluation_form,
        'document_form': document_form
    })
@login_required
@buyer_required
def bid_comparison(request, tender_id):
    tender = get_object_or_404(Tender, pk=tender_id)
    
    # Ensure user is the tender owner
    if tender.created_by != request.user:
        return HttpResponseForbidden("You don't have permission to compare bids for this tender.")
    
    bids = Bid.objects.filter(tender=tender).select_related('supplier', 'evaluation')
    
    return render(request, 'bidding/bid_comparison.html', {
        'tender': tender,
        'bids': bids
    })
@login_required
@buyer_required
def evaluate_bids(request):
    """Show all tenders with bids awaiting evaluation"""
    # Get tenders created by this user that have at least one pending bid
    tenders = Tender.objects.filter(
        created_by=request.user,
        bids__status='pending'  # Changed from 'submitted' to 'pending'
    ).distinct().annotate(
        total_bids=Count('bids'),
        pending_bids=Count('bids', filter=Q(bids__status='pending'))  # Also changed here
    )
    
    return render(request, 'bidding/evaluate_bids.html', {
        'tenders': tenders
    })

@login_required
@buyer_required
def evaluate_bids_for_tender(request, tender_id):
    """Show all bids for a specific tender for evaluation"""
    tender = get_object_or_404(Tender, pk=tender_id, created_by=request.user)
    
    # Get all bids for this tender
    bids = Bid.objects.filter(tender=tender).order_by('amount')
    
    # Calculate the average bid amount for reference
    avg_bid = bids.aggregate(avg=Avg('amount'))
    
    if request.method == 'POST':
        bid_id = request.POST.get('bid_id')
        action = request.POST.get('action')
        
        if bid_id and action:
            bid = get_object_or_404(Bid, pk=bid_id, tender=tender)
            
            if action == 'accept':
                # Accept this bid
                bid.status = 'accepted'
                bid.save()
                
                # Reject all other bids for this tender
                Bid.objects.filter(tender=tender).exclude(pk=bid_id).update(status='rejected')
                
                messages.success(request, f"Bid from {bid.supplier.get_full_name()} accepted. All other bids have been rejected.")
                
                # Redirect to contract creation
                return redirect('contracts:contract_create', bid_id=bid.id)
            
            elif action == 'reject':
                # Reject this bid
                bid.status = 'rejected'
                bid.save()
                messages.success(request, f"Bid from {bid.supplier.get_full_name()} rejected.")
            
        return redirect('bidding:evaluate_bids_for_tender', tender_id=tender_id)
    
    return render(request, 'bidding/evaluate_bids_for_tender.html', {
        'tender': tender,
        'bids': bids,
        'avg_bid': avg_bid['avg']
    })

@login_required
@buyer_required
def accepted_bids(request):
    """Show all accepted bids that could be turned into contracts"""
    # Get all accepted bids for tenders created by this user
    accepted_bids = Bid.objects.filter(
        tender__created_by=request.user,
        status='accepted'
    ).select_related('tender', 'supplier')
    
    # Filter out bids that already have contracts
    accepted_bids = [bid for bid in accepted_bids if not hasattr(bid, 'contract')]
    
    return render(request, 'bidding/accepted_bids.html', {
        'accepted_bids': accepted_bids
    })
@login_required
@supplier_required
def my_bids(request):
    """Display all bids submitted by the current supplier user"""
    bids = Bid.objects.filter(supplier=request.user).order_by('-created_at')
    
    return render(request, 'bidding/my_bids.html', {
        'bids': bids
    })