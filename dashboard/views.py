from datetime import timedelta
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.decorators import buyer_required, supplier_required, admin_required
from notifications.models import Notification
from tenders.models import Tender, TenderCategory
from django.db.models import Count, Q, Avg
from django.db.models import F, Count, Q, Avg, Sum
from bidding.models import Bid
from contracts.models import Contract, ContractStatus
from orders.models import Issue, Order, OrderStatus
from suppliers.models import SupplierProfile, SupplierCategory
from django.contrib.auth import get_user_model
from django.utils import timezone  # Import timezone properly

User = get_user_model()

@login_required
@buyer_required
def buyer_dashboard(request):
    user = request.user
    is_buyer = hasattr(user, 'is_buyer') and user.is_buyer
    if is_buyer:
        contracts = Contract.objects.filter(buyer=user)
        orders = Order.objects.filter(buyer=user)
    else:
        contracts = Contract.objects.filter(supplier=user)
        orders = Order.objects.filter(supplier=user)

    # Get recent contracts and orders
    recent_contracts = contracts.order_by('-created_at')[:5]
    recent_orders = orders.order_by('-created_at')[:5]

    # Get open issues
    open_issues = Issue.objects.filter(
        Q(raised_by=user) | Q(assigned_to=user),
        status__in=['open', 'in_progress']
    ).order_by('-created_at')[:5]

    # Calculate summary metrics
    active_contracts = contracts.filter(status__name='Active').count()
    pending_orders = orders.filter(status__name='Pending').count()
    total_order_value = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    # Get tender statistics
    active_tenders = Tender.objects.filter(created_by=user, is_active=True).count()
    closed_tenders = Tender.objects.filter(created_by=user, is_active=False).count()

    # Get recent tenders with additional context
    recent_tenders = Tender.objects.filter(created_by=user).order_by('-created_at')[:5]

    # Get contract statistics
    active_status = ContractStatus.objects.filter(name='Active').first()
    active_contracts = 0
    if active_status:
        active_contracts = Contract.objects.filter(
            buyer=user,
            status=active_status
        ).count()

    # Get recent contracts with supplier information
    recent_contracts = Contract.objects.filter(buyer=user).order_by('-created_at')[:5]

    # Get pending orders
    pending_status = OrderStatus.objects.filter(name='Pending').first()
    pending_orders = 0
    if pending_status:
        pending_orders = Order.objects.filter(
            contract__buyer=user,
            status=pending_status
        ).count()

    # Get tenders with pending bid evaluations
    pending_evaluation_tenders = Tender.objects.filter(
        created_by=user,
        is_active=True,
        submission_deadline__lt=timezone.now()
    ).annotate(
        num_bids=Count('bids'),
        num_evaluated=Count('bids', filter=Q(bids__status__in=['accepted', 'rejected']))
    ).filter(
        Q(num_bids__gt=0) &
        Q(num_bids__gt=F('num_evaluated'))
    )

    # Calculate cost savings (comparing winning bids to budget)
    contracts_with_savings = Contract.objects.filter(
        buyer=user,
        tender__budget__isnull=False
    ).annotate(
        savings=F('tender__budget') - F('total_value')
    )

    total_budget = contracts_with_savings.aggregate(
        total=Sum('tender__budget')
    )['total'] or 0

    total_actual = contracts_with_savings.aggregate(
        total=Sum('total_value')
    )['total'] or 0

    if total_budget > 0:
        savings_percentage = ((total_budget - total_actual) / total_budget) * 100
    else:
        savings_percentage = 0

    # Get budget utilization data
    budget_utilization = {
        'allocated': total_budget,
        'spent': total_actual,
        'remaining': total_budget - total_actual
    }


    # Get upcoming tender deadlines
    upcoming_deadlines = Tender.objects.filter(
        created_by=user,
        is_active=True,
        submission_deadline__gt=timezone.now()
    ).order_by('submission_deadline')[:3]

    # Get supplier performance metrics
    supplier_performance = Contract.objects.filter(
        buyer=user
    ).values(
        'supplier__username',
        'supplier__first_name',
        'supplier__last_name'
    ).annotate(
        contract_count=Count('id'),
        total_value=Sum('total_value'),

    ).order_by('-contract_count')[:5]

    # Get order statistics
    total_orders = orders.count()
    delivered_orders = orders.filter(status__name='Delivered').count()
    processing_orders = orders.filter(status__name='Processing').count()

    context = {
        'active_tenders': active_tenders,
        'closed_tenders': closed_tenders,
        'active_contracts': active_contracts,
        'pending_orders': pending_orders,
        'recent_tenders': recent_tenders,
        'recent_contracts': recent_contracts,
        'pending_evaluation_tenders': pending_evaluation_tenders,
        'savings_percentage': round(savings_percentage, 1),
        'budget_utilization': budget_utilization,
        'upcoming_deadlines': upcoming_deadlines,
        'supplier_performance': supplier_performance,
        'is_buyer': is_buyer,
        'open_issues': open_issues,
        'total_order_value': total_order_value,
        'recent_orders': recent_orders,
        'total_orders': total_orders,
        'delivered_orders': delivered_orders,
        'processing_orders': processing_orders,
    }
    return render(request, 'dashboard/buyer_dashboard.html', context)

@login_required
@supplier_required
def supplier_dashboard(request):
    user = request.user
    
    try:
        supplier_profile = user.supplier_profile
        # Get supplier categories
        supplier_categories = supplier_profile.categories.all()
        
        # Get tender categories that match supplier categories by name
        tender_categories = TenderCategory.objects.filter(name__in=supplier_categories.values_list('name', flat=True))

        # Get available tender list based on matching categories
        if tender_categories.exists():
            available_tender_list = Tender.objects.filter(
                is_active=True,
                submission_deadline__gt=timezone.now(),
                categories__in=tender_categories
            ).distinct().order_by('-created_at')[:5]
        else:
            # If no matching categories, show all active tenders
            available_tender_list = Tender.objects.filter(
                is_active=True,
                submission_deadline__gt=timezone.now()
            ).distinct().order_by('-created_at')[:5]
        
        # Count available tenders (for display in card)
        available_tenders_count = available_tender_list.count()
        
        # Mark tenders where the user already submitted a bid
        for tender in available_tender_list:
            tender.has_user_bid = Bid.objects.filter(
                tender=tender,
                supplier=user
            ).exists()
        
        # Get bid statistics
        submitted_bids = Bid.objects.filter(supplier=user).count()
        won_bids = Bid.objects.filter(supplier=user, status='accepted').count()
        
        # Calculate bid success rate
        if submitted_bids > 0:
            bid_success_rate = int((won_bids / submitted_bids) * 100)
        else:
            bid_success_rate = 0
        
        # Get contract information
        active_contracts = Contract.objects.filter(supplier=user, status__name='Active').count()
        supplier_contracts = Contract.objects.filter(supplier=user).order_by('-created_at')[:5]
        
        # Get recent bids with status information
        recent_bids = Bid.objects.filter(supplier=user).order_by('-created_at')[:5]
        
        # Calculate average bid value
        avg_bid = Bid.objects.filter(supplier=user).aggregate(avg=Avg('amount'))
        avg_bid_value = avg_bid['avg'] if avg_bid['avg'] else 0
        
        # Get total contract value
        total_value = Contract.objects.filter(supplier=user).aggregate(
            total=Sum('total_value')
        )
        total_contract_value = total_value['total'] if total_value['total'] else 0
        
        # Get notifications
        notifications = []
        if 'Notification' in globals():  # Check if Notification model exists
            notifications = Notification.objects.filter(
                recipient=user,
                read=False
            ).order_by('-created_at')[:5]
        
        # Get recommended tenders based on past bidding history and supplier categories
        bid_categories = Bid.objects.filter(
            supplier=user
        ).values_list('tender__categories__id', flat=True).distinct()
        
        # Combine bid history categories with supplier profile categories for recommendations
        supplier_category_ids = supplier_profile.categories.values_list('id', flat=True)
        
        # Find matching tender categories by name
        matching_tender_category_ids = tender_categories.values_list('id', flat=True)
        
        # Combined category IDs for recommendations
        recommendation_category_ids = list(bid_categories) + list(matching_tender_category_ids)
        
        if recommendation_category_ids:
            recommended_tenders = Tender.objects.filter(
                is_active=True,
                submission_deadline__gt=timezone.now(),
                categories__id__in=recommendation_category_ids
            ).exclude(
                id__in=Bid.objects.filter(supplier=user).values_list('tender__id', flat=True)
            ).distinct()[:4]
        else:
            # If no categories to recommend from, show random active tenders
            recommended_tenders = Tender.objects.filter(
                is_active=True,
                submission_deadline__gt=timezone.now()
            ).exclude(
                id__in=Bid.objects.filter(supplier=user).values_list('tender__id', flat=True)
            ).distinct()[:4]
        
        # Get upcoming bid deadlines
        upcoming_deadlines = Tender.objects.filter(
            is_active=True,
            submission_deadline__gt=timezone.now(),
            submission_deadline__lte=timezone.now() + timedelta(days=7),
            bids__supplier=user
        ).distinct()[:3]
        
        context = {
            'available_tenders': available_tenders_count,
            'available_tender_list': available_tender_list,
            'submitted_bids': submitted_bids,
            'won_bids': won_bids,
            'active_contracts': active_contracts,
            'recent_bids': recent_bids,
            'supplier_contracts': supplier_contracts,
            'notifications': notifications,
            'recommended_tenders': recommended_tenders,
            'upcoming_deadlines': upcoming_deadlines,
            'bid_success_rate': bid_success_rate,
            'avg_bid_value': round(avg_bid_value, 2),
            'total_contract_value': round(total_contract_value, 2),
        }
        return render(request, 'dashboard/supplier_dashboard.html', context)
        
    except SupplierProfile.DoesNotExist:
        return render(request, 'dashboard/no_supplier_profile.html')
    except Exception as e:
        print(f"Error in supplier_dashboard: {e}")
        return render(request, 'dashboard/error.html', {'error': 'Could not retrieve dashboard data.'})

@login_required
@admin_required
def admin_dashboard(request):
    # Get system-wide statistics for admin
    total_users = User.objects.count()
    total_buyers = User.objects.filter(user_type='buyer').count()
    total_suppliers = User.objects.filter(user_type='supplier').count()
    active_tenders = Tender.objects.filter(is_active=True).count()
    total_contracts = Contract.objects.count()
    
    context = {
        'total_users': total_users,
        'total_buyers': total_buyers,
        'total_suppliers': total_suppliers,
        'active_tenders': active_tenders,
        'total_contracts': total_contracts,
        'recent_users': User.objects.order_by('-date_joined')[:10],
        'recent_tenders': Tender.objects.order_by('-created_at')[:10],
    }
    return render(request, 'dashboard/admin_dashboard.html', context)