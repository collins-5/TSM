from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list, name='notification_list'),
    path('<int:pk>/', views.notification_detail, name='notification_detail'),
    path('<int:pk>/mark-read/', views.mark_notification_read, name='mark_notification_read'),
    path('mark-all-read/', views.mark_all_read, name='mark_all_read'),
]