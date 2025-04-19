from django.urls import path
from . import views

app_name = 'suppliers'
urlpatterns = [
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/<int:pk>/', views.supplier_detail, name='supplier_detail'),
    path('supplier/edit/', views.supplier_profile_edit, name='supplier_profile_edit'),
    path('suppliers/<int:pk>/rate/', views.supplier_rating, name='supplier_rating'),
    path('supplier/document/<int:pk>/delete/', views.supplier_document_delete, name='supplier_document_delete'),
]