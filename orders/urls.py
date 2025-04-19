from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Order URLs
    path('create/<int:contract_id>/', views.order_create, name='order_create'),
    path('', views.order_list, name='order_list'),
    path('<int:pk>/', views.order_detail, name='order_detail'),
    path('<int:pk>/update-status/', views.order_update_status, name='order_update_status'),
    
    # Issue URLs
    path('issue/<int:pk>/', views.issue_detail, name='issue_detail'),
    path('<int:order_id>/issue/create/', views.issue_create, name='issue_create'),
    path('issues/', views.issue_list, name='issue_list'),
    #pdf URLs
    path('<int:order_id>/print/', views.print_order, name='print_order'),
    path('<int:order_id>/pdf/', views.download_order_pdf, name='download_order_pdf'),
]