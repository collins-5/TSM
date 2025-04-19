from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Q
from django.utils import timezone
import uuid

from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.template.loader import get_template
from django.utils import timezone
from django.db.models import Q

from .models import Order, OrderItem

from .models import Order, OrderItem, OrderStatus, Issue
from .forms import OrderForm, OrderItemFormSet, IssueForm, IssueUpdateForm
from contracts.models import Contract
from accounts.decorators import buyer_required
from notifications.services import create_notification

@login_required
@buyer_required
def order_create(request, contract_id):
    """Create a new order based on a contract"""
    contract = get_object_or_404(Contract, pk=contract_id)
    
    # Check if user has permission to create order for this contract
    if contract.buyer != request.user:
        return HttpResponseForbidden("You don't have permission to create an order for this contract.")
    # Check if contract is in a valid state for ordering
    if contract.status.name not in ["Active", "Ongoing"]:
        messages.error(request, "Orders can only be created for active contracts.")
        return redirect('contracts:contract_detail', pk=contract_id)
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.contract = contract
            order.buyer = request.user
            order.supplier = contract.supplier
            
            # Generate order number
            order.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
            
            # Set initial status
            default_status = OrderStatus.objects.get_or_create(name="Pending")[0]
            order.status = default_status
            
            # Calculate total from items
            order.total_amount = 0  # Will be updated after item formset is saved
            
            order.save()
            
            # Handle order items
            formset = OrderItemFormSet(request.POST, instance=order)
            if formset.is_valid():
                formset.save()
                
                # Update order total
                total = sum(item.total_price for item in order.items.all())
                order.total_amount = total
                order.save()
                
                messages.success(request, "Order created successfully.")
                return redirect('orders:order_detail', pk=order.pk)
            else:
                # If formset invalid, delete the order to prevent orphaned records
                order.delete()
                messages.error(request, "Please correct the errors in your order items.")
        else:
            messages.error(request, "Please correct the errors in your order form.")
    else:
        form = OrderForm()
        formset = OrderItemFormSet()
    
    return render(request, 'orders/order_form.html', {
        'form': form,
        'formset': formset,
        'contract': contract
    })

@login_required
def order_list(request):
    """List orders relevant to the current user"""
    if request.user.is_staff:
        # Admin can see all orders
        orders = Order.objects.all()
    else:
        # Regular users see only their orders
        orders = Order.objects.filter(
            Q(buyer=request.user) | Q(supplier=request.user)
        )
    
    return render(request, 'orders/order_list.html', {
        'orders': orders
    })

@login_required
def order_detail(request, pk):
    """View an order's details"""
    order = get_object_or_404(Order, pk=pk)
    
    # Check if user has permission to view this order
    if not (order.buyer == request.user or order.supplier == request.user or request.user.is_staff):
        return HttpResponseForbidden("You don't have permission to view this order.")
    
    items = order.items.all()
    issues = order.issues.all()
    
    # Issue form for creating new issues
    issue_form = None
    if request.method == 'POST' and 'create_issue' in request.POST:
        issue_form = IssueForm(request.POST)
        if issue_form.is_valid():
            issue = issue_form.save(commit=False)
            issue.order = order
            issue.raised_by = request.user
            
            # Auto-assign to appropriate party
            if request.user == order.buyer:
                issue.assigned_to = order.supplier
            else:
                issue.assigned_to = order.buyer
                
            issue.save()
            messages.success(request, "Issue reported successfully.")
            return redirect('orders:order_detail', pk=pk)
    else:
        issue_form = IssueForm()
    
    return render(request, 'orders/order_detail.html', {
        'order': order,
        'items': items,
        'issues': issues,
        'issue_form': issue_form,
        'is_buyer': order.buyer == request.user,
        'is_supplier': order.supplier == request.user
    })

@login_required
@buyer_required
def order_update_status(request, pk):
    """Update the status of an order"""
    order = get_object_or_404(Order, pk=pk)

    # Check if user has permission to update this order
    if not (order.buyer == request.user or request.user.is_staff):
        return HttpResponseForbidden("You don't have permission to update this order.")

    if request.method == 'POST':
        new_status_id = request.POST.get('status_id')
        if new_status_id:
            status = get_object_or_404(OrderStatus, pk=new_status_id)
            order.status = status

            if status.name == "Delivered":
                order.delivered_at = timezone.now()
                messages.success(request, f"Order marked as '{status.name}' and delivery confirmed.")

                # --- Send notification to the supplier ---
                notification_title = f"Order #{order.order_number} Delivered"
                notification_message = f"Buyer {request.user.get_full_name() or request.user.username} has confirmed the delivery for Order #{order.order_number}."
                create_notification(
                    recipient=order.supplier,
                    notification_type_name='order_delivery_confirmed',  # Choose a relevant type
                    title=notification_title,
                    message=notification_message,
                    link=f'/orders/{order.id}/'  # Link to the order detail page
                )

            else:
                messages.success(request, f"Order status updated to '{status.name}'.")

            order.save()
        else:
            messages.error(request, "Invalid status selected.")

        return redirect('orders:order_detail', pk=pk)

    # Get all possible statuses for the dropdown
    statuses = OrderStatus.objects.all()

    return render(request, 'orders/order_status_update.html', {
        'order': order,
        'statuses': statuses
    })


@login_required
def issue_detail(request, pk):
    """View and manage an issue"""
    issue = get_object_or_404(Issue, pk=pk)
    order = issue.order
    
    # Check if user has permission to view this issue
    if not (order.buyer == request.user or order.supplier == request.user or request.user.is_staff):
        return HttpResponseForbidden("You don't have permission to view this issue.")
    
    # Issue update form
    if request.method == 'POST':
        form = IssueUpdateForm(request.POST, instance=issue)
        if form.is_valid():
            updated_issue = form.save(commit=False)
            
            # If status changed to resolved, set resolved_at timestamp
            if updated_issue.status == 'resolved' and issue.status != 'resolved':
                updated_issue.resolved_at = timezone.now()
                
            updated_issue.save()
            messages.success(request, "Issue updated successfully.")
            return redirect('issue_detail', pk=pk)
    else:
        form = IssueUpdateForm(instance=issue)
    
    return render(request, 'orders/issue_detail.html', {
        'issue': issue,
        'order': order,
        'form': form,
        'is_creator': issue.raised_by == request.user,
        'is_assignee': issue.assigned_to == request.user
    })

@login_required
def issue_create(request, order_id):
    """Create a new issue for an order"""
    order = get_object_or_404(Order, pk=order_id)
    
    # Check if user has permission to create issues for this order
    if not (order.buyer == request.user or order.supplier == request.user):
        return HttpResponseForbidden("You don't have permission to create issues for this order.")
    
    if request.method == 'POST':
        form = IssueForm(request.POST)
        if form.is_valid():
            issue = form.save(commit=False)
            issue.order = order
            issue.raised_by = request.user
            
            # Auto-assign to appropriate party
            if request.user == order.buyer:
                issue.assigned_to = order.supplier
            else:
                issue.assigned_to = order.buyer
                
            issue.save()
            messages.success(request, "Issue reported successfully.")
            return redirect('orders:order_detail', pk=order_id)
    else:
        form = IssueForm()
    
    return render(request, 'orders/issue_form.html', {
        'form': form,
        'order': order
    })

@login_required
def issue_list(request):
    """List issues relevant to the current user"""
    if request.user.is_staff:
        # Admin can see all issues
        issues = Issue.objects.all()
    else:
        # Regular users see only their issues
        issues = Issue.objects.filter(
            Q(raised_by=request.user) | Q(assigned_to=request.user)
        )
    
    return render(request, 'orders/issue_list.html', {
        'issues': issues
    })

@login_required
def print_order(request, order_id):
    """Display a print-friendly version of an order"""
    order = get_object_or_404(Order, id=order_id)
    
    # Security check - only allow buyer, supplier, or admin to view
    if not (request.user == order.buyer or request.user == order.supplier or request.user.is_staff):
        return HttpResponseForbidden("You don't have permission to view this order")
    
    # Get additional data like line items
    order_items = OrderItem.objects.filter(order=order)
    
    return render(request, 'orders/print_order.html', {
        'order': order,
        'order_items': order_items,
        'now': timezone.now(),  # Pass current time for the timestamp
    })

@login_required
def download_order_pdf(request, order_id):
    """Generate and download a PDF of the order"""
    try:
        # First make sure we have xhtml2pdf installed
        import xhtml2pdf.pisa as pisa
        from io import BytesIO
    except ImportError:
        return HttpResponse("PDF generation requires the xhtml2pdf package. Please install it with: pip install xhtml2pdf", 
                          status=500, content_type="text/plain")
    
    order = get_object_or_404(Order, id=order_id)
    
    # Security check - only allow buyer, supplier, or admin to download
    if not (request.user == order.buyer or request.user == order.supplier or request.user.is_staff):
        return HttpResponseForbidden("You don't have permission to view this order")
    
    # Get additional data like line items
    order_items = OrderItem.objects.filter(order=order)
    
    # Render the template to HTML
    template = get_template('orders/pdf_order.html')
    html = template.render({
        'order': order,
        'order_items': order_items,
        'now': timezone.now(),  # Pass current time for the timestamp
        'STATIC_URL': settings.STATIC_URL,  # For images in the PDF
    })
    
    # Create a PDF from the HTML
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    
    if not pdf.err:
        # PDF created successfully
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        filename = f"Order_{order.order_number}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
    # Error in PDF generation
    return HttpResponse("Error generating PDF", status=500)