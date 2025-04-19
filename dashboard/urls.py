# dashboard/urls.py
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # path('', views.home, name='home'),
    path('buyer/', views.buyer_dashboard, name='buyer_dashboard'),
    path('supplier/', views.supplier_dashboard, name='supplier_dashboard'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
]