from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('', views.document_list, name='document_list'),
    path('upload/', views.document_upload, name='document_upload'),
    path('<int:pk>/', views.document_detail, name='document_detail'),
    path('<int:pk>/download/', views.document_download, name='document_download'),
    path('<int:pk>/delete/', views.document_delete, name='document_delete'),
    path('<int:pk>/update/', views.document_update, name='document_update'),
]