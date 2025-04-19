from django.urls import path
from . import views

app_name = 'contracts'

urlpatterns = [
    path('list/', views.contract_list, name='contract_list'),
    path('from-bid/<int:bid_id>/', views.contract_create, name='contract_create'),
    path('<int:pk>/', views.contract_detail, name='contract_detail'),
    path('<int:pk>/update/', views.contract_update, name='contract_update'),
    path('<int:pk>/status-update/', views.contract_status_update, name='contract_status_update'),
    path('my/', views.contract_list, name='my_contracts'),  # Alias for contract_list with filter
    path('<int:pk>/terminate/', views.contract_terminate, name='contract_terminate'),
]