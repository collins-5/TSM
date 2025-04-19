from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Notification

@login_required
def notification_list(request):
    notifications = request.user.notifications.all()
    unread_count = notifications.filter(read=False).count()
    
    paginator = Paginator(notifications, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'notifications/notification_list.html', {
        'page_obj': page_obj,
        'unread_count': unread_count
    })

@login_required
def notification_detail(request, pk):
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    
    if not notification.read:
        notification.read = True
        notification.read_at = timezone.now()
        notification.save()
    
    return render(request, 'notifications/notification_detail.html', {
        'notification': notification
    })

@login_required
def mark_notification_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.read = True
    notification.read_at = timezone.now()
    notification.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    return redirect('notifications:notification_list')

@login_required
def mark_all_read(request):
    request.user.notifications.filter(read=False).update(
        read=True, 
        read_at=timezone.now()
    )
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    return redirect('notifications:notification_list')