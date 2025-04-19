# tenders/urls.py
from django.urls import path
from . import views

app_name = 'tenders'

urlpatterns = [
    path('', views.tender_list, name='tender_list'),
    path('tender/<int:pk>/close/', views.tender_close, name='tender_close'),
    path('create/', views.tender_create, name='tender_create'),
    path('<int:pk>/', views.tender_detail, name='tender_detail'),
    path('<int:pk>/update/', views.tender_update, name='tender_update'),
    path('<int:pk>/add-document/', views.tender_add_document, name='tender_add_document'),
    path('categories/', views.category_list, name='category_list'),
]