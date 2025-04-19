from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('buyer/orders/', include('orders.urls', namespace='orders')),
    path('accounts/', include('accounts.urls')),
    path('tenders/', include('tenders.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('bidding/', include('bidding.urls')),
    
    path('contracts/', include('contracts.urls')),
    path('orders/', include('orders.urls')),
    path('suppliers/', include('suppliers.urls')),
    path('notifications/', include('notifications.urls')),
    path('documents/', include('documents.urls')),
    path('api/', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)