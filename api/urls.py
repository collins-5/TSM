from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, 
    TenderViewSet,
    BidViewSet,
    ContractViewSet,
    OrderViewSet,
    SupplierViewSet,
    NotificationViewSet,
    DocumentViewSet
)

router = DefaultRouter()
router.register('users', UserViewSet)
router.register('tenders', TenderViewSet)
router.register('bids', BidViewSet)
router.register('contracts', ContractViewSet)
router.register('orders', OrderViewSet)
router.register('suppliers', SupplierViewSet)
router.register('notifications', NotificationViewSet)
router.register('documents', DocumentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),
]