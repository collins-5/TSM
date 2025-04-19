from functools import wraps
from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from django.urls import reverse
from django.contrib import messages


def buyer_required(view_func):
    """Decorator to require buyer user type"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_buyer:
            return view_func(request, *args, **kwargs)
        messages.error(request, "Access denied. Buyer permissions required.")
        return HttpResponseForbidden("Buyer access required")
    return _wrapped_view


def supplier_required(view_func):
    """Decorator to require supplier user type"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_supplier:
            return view_func(request, *args, **kwargs)
        messages.error(request, "Access denied. Supplier permissions required.")
        return HttpResponseForbidden("Supplier access required")
    return _wrapped_view


def admin_required(view_func):
    """Decorator to require admin user type or staff status"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and (request.user.is_admin_user or request.user.is_staff):
            return view_func(request, *args, **kwargs)
        messages.error(request, "Access denied. Administrator permissions required.")
        return HttpResponseForbidden("Admin access required")
    return _wrapped_view


def tender_owner_required(view_func):
    """Decorator to require tender owner access"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        from tenders.models import Tender
        
        tender_id = kwargs.get('tender_id')
        if not tender_id:
            return HttpResponseForbidden("Tender not specified")
        
        try:
            tender = Tender.objects.get(id=tender_id)
            if request.user.is_authenticated and (
                request.user.is_staff or 
                request.user.is_admin_user or 
                (request.user.is_buyer and tender.created_by == request.user)
            ):
                return view_func(request, *args, **kwargs)
        except Tender.DoesNotExist:
            pass
        
        messages.error(request, "Access denied. You don't have permission to access this tender.")
        return HttpResponseForbidden("Tender owner access required")
    return _wrapped_view


def contract_participant_required(view_func):
    """Decorator to require contract participant access"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        from contracts.models import Contract
        
        contract_id = kwargs.get('contract_id')
        if not contract_id:
            return HttpResponseForbidden("Contract not specified")
        
        try:
            contract = Contract.objects.get(id=contract_id)
            if request.user.is_authenticated and (
                request.user.is_staff or 
                request.user.is_admin_user or 
                (request.user.is_buyer and contract.created_by == request.user) or
                (request.user.is_supplier and contract.supplier == request.user)
            ):
                return view_func(request, *args, **kwargs)
        except Contract.DoesNotExist:
            pass
        
        messages.error(request, "Access denied. You don't have permission to access this contract.")
        return HttpResponseForbidden("Contract participant access required")
    return _wrapped_view