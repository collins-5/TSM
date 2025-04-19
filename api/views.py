from datetime import timezone
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend

from accounts import models
from accounts.models import UserProfile
from api.serializers.document_serializers import DocumentSerializer
from api.serializers.notification_serializers import NotificationSerializer
from tenders.models import Tender, TenderCategory, TenderStage, TenderDocument
from bidding.models import Bid, BidDocument, BidEvaluation
from contracts.models import Contract, ContractDocument, ContractStatus
from orders.models import Order, OrderItem, OrderStatus, Issue
from suppliers.models import SupplierProfile, SupplierCategory, SupplierRating
from notifications.models import Notification, NotificationType
from documents.models import Document, DocumentCategory

from .serializers.user_serializers import UserSerializer, UserProfileSerializer
from .serializers.tender_serializers import TenderSerializer, TenderCategorySerializer
from .serializers.bid_serializers import BidSerializer, BidDocumentSerializer
from .serializers.contract_serializers import ContractSerializer, ContractDocumentSerializer
from .serializers.order_serializers import OrderSerializer, OrderItemSerializer
from .serializers.supplier_serializers import SupplierProfileSerializer, SupplierRatingSerializer
from .permissions import IsOwnerOrAdmin, IsBuyerOrReadOnly, IsSupplierOrReadOnly, IsParticipantOrReadOnly

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def profile(self, request):
        try:
            profile = request.user.userprofile
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            return Response({'detail': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

class TenderViewSet(viewsets.ModelViewSet):
    queryset = Tender.objects.all()
    serializer_class = TenderSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsBuyerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'stage']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'deadline']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        tender = self.get_object()
        documents = tender.documents.all()
        serializer = TenderDocumentSerializer(documents, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def bids(self, request, pk=None):
        tender = self.get_object()
        
        # Only tender owner can see all bids
        if tender.created_by != request.user and not request.user.is_staff:
            return Response({'detail': 'Not authorized to view bids'}, status=status.HTTP_403_FORBIDDEN)
        
        bids = tender.bids.all()
        serializer = BidSerializer(bids, many=True)
        return Response(serializer.data)

class BidViewSet(viewsets.ModelViewSet):
    queryset = Bid.objects.all()
    serializer_class = BidSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipantOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['tender', 'status']
    ordering_fields = ['created_at', 'bid_amount']
    
    def perform_create(self, serializer):
        serializer.save(supplier=self.request.user)
    
    def get_queryset(self):
        user = self.request.user
        
        # Admin sees all
        if user.is_staff:
            return Bid.objects.all()
        
        # Filter bids that user has access to (as supplier or buyer)
        if hasattr(user, 'userprofile'):
            if user.userprofile.user_type == 'supplier':
                return Bid.objects.filter(supplier=user)
            elif user.userprofile.user_type == 'buyer':
                return Bid.objects.filter(tender__created_by=user)
        
        return Bid.objects.none()
    
    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        bid = self.get_object()
        documents = bid.documents.all()
        serializer = BidDocumentSerializer(documents, many=True)
        return Response(serializer.data)

class ContractViewSet(viewsets.ModelViewSet):
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipantOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['created_at', 'start_date', 'end_date']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def get_queryset(self):
        user = self.request.user
        
        # Admin sees all
        if user.is_staff:
            return Contract.objects.all()
        
        # Filter contracts that user participates in
        return Contract.objects.filter(
            models.Q(tender__created_by=user) | models.Q(supplier=user)
        )
    
    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        contract = self.get_object()
        documents = contract.documents.all()
        serializer = ContractDocumentSerializer(documents, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def orders(self, request, pk=None):
        contract = self.get_object()
        orders = contract.orders.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipantOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'contract']
    ordering_fields = ['created_at', 'delivery_date']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    def get_queryset(self):
        user = self.request.user
        
        # Admin sees all
        if user.is_staff:
            return Order.objects.all()
        
        # Filter orders that user participates in
        from django.db.models import Q
        return Order.objects.filter(
            Q(contract__tender__created_by=user) | Q(contract__supplier=user)
        )
    
    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        order = self.get_object()
        items = order.items.all()
        serializer = OrderItemSerializer(items, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def issues(self, request, pk=None):
        order = self.get_object()
        issues = order.issues.all()
        from .serializers.order_serializers import IssueSerializer
        serializer = IssueSerializer(issues, many=True)
        return Response(serializer.data)

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = SupplierProfile.objects.all()
    serializer_class = SupplierProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'company_name']
    
    @action(detail=True, methods=['post'], permission_classes=[IsBuyerOrReadOnly])
    def rate(self, request, pk=None):
        supplier = self.get_object()
        from .serializers.supplier_serializers import SupplierRatingSerializer
        
        serializer = SupplierRatingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                supplier=supplier,
                rated_by=request.user
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def ratings(self, request, pk=None):
        supplier = self.get_object()
        ratings = supplier.ratings.all()
        from .serializers.supplier_serializers import SupplierRatingSerializer
        serializer = SupplierRatingSerializer(ratings, many=True)
        return Response(serializer.data)

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']
    
    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.read = True
        notification.read_at = timezone.now()
        notification.save()
        serializer = self.get_serializer(notification)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        queryset = self.get_queryset().filter(read=False)
        queryset.update(read=True, read_at=timezone.now())
        return Response({'status': 'success'})

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'visibility']
    search_fields = ['title', 'description']
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)
    
    def get_queryset(self):
        user = self.request.user
        
        # Admin sees all
        if user.is_staff:
            return Document.objects.all()
        
        # Get all public documents
        public_docs = Document.objects.filter(visibility='public')
        
        # Get user's own documents
        private_docs = Document.objects.filter(uploaded_by=user)
        
        # Get documents shared with user
        restricted_docs = user.accessible_documents.all()
        
        # Combine and remove duplicates
        from django.db.models import Q
        return (public_docs | private_docs | restricted_docs).distinct()
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        document = self.get_object()
        # Logic for downloading would be implemented here
        # For API it might be a redirect to the file URL or serving the file
        return Response({'file_url': document.file.url})