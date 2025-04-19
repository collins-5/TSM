from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Q

from .models import Contract, ContractStatus, ContractDocument
from .forms import ContractForm, ContractFromBidForm, ContractDocumentForm
from tenders.models import Tender
from bidding.models import Bid
from accounts.decorators import buyer_required

@login_required
@buyer_required
def contract_create(request, bid_id):
    """Create a new contract based on a winning bid"""
    # Get the bid and verify permissions
    bid = get_object_or_404(Bid, pk=bid_id)
    tender = bid.tender
    
    # Check if user is tender owner
    if tender.created_by != request.user:
        return HttpResponseForbidden("You don't have permission to create a contract for this tender.")
    
    # Check if tender already has a contract
    existing_contract = Contract.objects.filter(tender=tender).first()
    if existing_contract:
        messages.warning(request, "A contract already exists for this tender.")
        return redirect('contracts:contract_detail', pk=existing_contract.pk)
    
    # Pre-fill contract info from bid and tender
    initial_data = {
        'title': f"Contract for {tender.title}",
        'scope_of_work': tender.description,
        'total_value': bid.amount,
    }
    
    if request.method == 'POST':
        form = ContractForm(request.POST)
        if form.is_valid():
            contract = form.save(commit=False)
            contract.buyer = request.user
            contract.tender = tender
            contract.winning_bid = bid
            contract.supplier = bid.supplier
            
            # Set initial status
            default_status = ContractStatus.objects.get_or_create(name="Draft")[0]
            contract.status = default_status
            
            contract.save()
            
            # Update bid status to show it was accepted
            bid.status = 'accepted'
            bid.save()
            
            messages.success(request, "Contract created successfully.")
            return redirect('contracts:contract_detail', pk=contract.pk)
    else:
        form = ContractForm(initial=initial_data)
    
    return render(request, 'contracts/contract_form.html', {
        'form': form,
        'tender': tender,
        'winning_bid': bid,
        'supplier': bid.supplier
    })

@login_required
def contract_list(request):
    """List contracts relevant to the current user"""
    if request.user.is_staff:
        # Admin can see all contracts
        contracts = Contract.objects.all()
    else:
        # Regular users see only their contracts
        contracts = Contract.objects.filter(
            Q(buyer=request.user) | Q(supplier=request.user)
        )
    
    # Get all statuses for filtering
    contract_statuses = ContractStatus.objects.all()
    
    # Add the user role for contextual UI elements
    is_buyer = hasattr(request.user, 'is_buyer') and request.user.is_buyer
    
    return render(request, 'contracts/contract_list.html', {
        'contracts': contracts,
        'contract_statuses': contract_statuses,
        'is_buyer': is_buyer
    })

@login_required
def contract_detail(request, pk):
    """View a contract's details"""
    contract = get_object_or_404(Contract, pk=pk)
    
    # Check if user has permission to view this contract
    if not (contract.buyer == request.user or contract.supplier == request.user or request.user.is_staff):
        return HttpResponseForbidden("You don't have permission to view this contract.")
    
    documents = contract.documents.all()
    
    # Document upload form for authorized users
    document_form = None
    can_upload = contract.buyer == request.user  # Only buyer can upload docs
    
    if can_upload:
        if request.method == 'POST' and 'upload' in request.POST:
            document_form = ContractDocumentForm(request.POST, request.FILES)
            if document_form.is_valid():
                doc = document_form.save(commit=False)
                doc.contract = contract
                doc.uploaded_by = request.user
                doc.save()
                messages.success(request, "Document uploaded successfully.")
                return redirect('contracts:contract_detail', pk=pk)
        else:
            document_form = ContractDocumentForm()
    
    return render(request, 'contracts/contract_detail.html', {
        'contract': contract,
        'documents': documents,
        'can_upload': can_upload,
        'document_form': document_form,
        'is_buyer': contract.buyer == request.user,
        'is_supplier': contract.supplier == request.user
    })

@login_required
@buyer_required
def contract_update(request, pk):
    """Update an existing contract"""
    contract = get_object_or_404(Contract, pk=pk)
    
    # Only the contract buyer can update it
    if contract.buyer != request.user:
        return HttpResponseForbidden("You don't have permission to update this contract.")
    
    if request.method == 'POST':
        form = ContractForm(request.POST, instance=contract)
        if form.is_valid():
            form.save()
            messages.success(request, "Contract updated successfully.")
            return redirect('contracts:contract_detail', pk=pk)
    else:
        form = ContractForm(instance=contract)
    
    return render(request, 'contracts/contract_form.html', {
        'form': form,
        'contract': contract,
        'is_update': True
    })

@login_required
@buyer_required
def contract_status_update(request, pk):
    """Update the status of a contract"""
    contract = get_object_or_404(Contract, pk=pk)
    
    # Only the contract buyer can update status
    if contract.buyer != request.user:
        return HttpResponseForbidden("You don't have permission to update this contract status.")
    
    if request.method == 'POST':
        new_status_id = request.POST.get('status_id')
        if new_status_id:
            status = get_object_or_404(ContractStatus, pk=new_status_id)
            contract.status = status
            contract.save()
            messages.success(request, f"Contract status updated to '{status.name}'.")
        else:
            messages.error(request, "Invalid status selected.")
        
        return redirect('contracts:contract_detail', pk=pk)
    
    # Get all possible statuses for the dropdown
    statuses = ContractStatus.objects.all()
    
    return render(request, 'contracts/contract_status_update.html', {
        'contract': contract,
        'statuses': statuses
    })

@login_required
@buyer_required
def contract_terminate(request, pk):
    """Terminate or delete a contract"""
    contract = get_object_or_404(Contract, pk=pk)
    
    # Only the contract buyer can terminate it
    if contract.buyer != request.user:
        return HttpResponseForbidden("You don't have permission to terminate this contract.")
    
    if request.method == 'POST':
        reason = request.POST.get('termination_reason', '')
        
        # Instead of actually deleting, update status to "Terminated"
        terminated_status = ContractStatus.objects.get_or_create(name="Terminated")[0]
        contract.status = terminated_status
        contract.termination_reason = reason  # You'll need to add this field to the Contract model
        contract.save()
        
        messages.success(request, "Contract has been terminated.")
        return redirect('contracts:contract_list')
    
    return render(request, 'contracts/contract_terminate.html', {
        'contract': contract
    })