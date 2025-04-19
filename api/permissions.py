from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins to access it.
    """
    def has_object_permission(self, request, view, obj):
        # Admin permissions
        if request.user.is_staff:
            return True
        
        # Check if obj has an owner field (different models use different field names)
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'uploaded_by'):
            return obj.uploaded_by == request.user
        
        # If we don't know how to determine ownership, deny permission
        return False

class IsBuyerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow buyers to create/edit objects.
    """
    def has_permission(self, request, view):
        # Allow read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to buyers
        return request.user.is_authenticated and hasattr(request.user, 'userprofile') and request.user.userprofile.user_type == 'buyer'

class IsSupplierOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow suppliers to create/edit objects.
    """
    def has_permission(self, request, view):
        # Allow read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to suppliers
        return request.user.is_authenticated and hasattr(request.user, 'userprofile') and request.user.userprofile.user_type == 'supplier'

class IsParticipantOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow participants to view detailed information.
    """
    def has_object_permission(self, request, view, obj):
        # Admin permissions
        if request.user.is_staff:
            return True
        
        # For contracts
        if hasattr(obj, 'tender') and hasattr(obj.tender, 'created_by'):
            if obj.tender.created_by == request.user:
                return True
            
            # Check if user is the winner
            if hasattr(obj, 'supplier') and obj.supplier == request.user:
                return True
        
        # For bids
        if hasattr(obj, 'tender') and hasattr(obj, 'supplier'):
            if obj.tender.created_by == request.user or obj.supplier == request.user:
                return True
        
        # For orders
        if hasattr(obj, 'contract'):
            if obj.contract.tender.created_by == request.user or obj.contract.supplier == request.user:
                return True
        
        # If safe method, allow if object is public
        if request.method in permissions.SAFE_METHODS and hasattr(obj, 'is_public') and obj.is_public:
            return True
        
        return False