from django.urls import path
from . import views
app_name = 'bidding'
urlpatterns = [
    path('tender/<int:tender_id>/bid/create/', views.bid_create, name='bid_create'),
    path('bid/<int:pk>/update/', views.bid_update, name='bid_update'),
    path('tender/<int:tender_id>/bids/', views.bid_list, name='bid_list'),
    path('bid/<int:pk>/', views.bid_detail, name='bid_detail'),
    path('tender/<int:tender_id>/bid-comparison/', views.bid_comparison, name='bid_comparison'),
    path('evaluate/', views.evaluate_bids, name='evaluate_bids'),
    path('evaluate/', views.evaluate_bids, name='evaluate_bids'),
    path('evaluate/<int:tender_id>/', views.evaluate_bids_for_tender, name='evaluate_bids_for_tender'),
    path('my/', views.my_bids, name='my_bids'),  # List of bids submitted by the current user
    # path('submit/<int:tender_id>/', views.submit_bid, name='submit_bid'),
    # path('view/<int:bid_id>/', views.view_bid, name='view_bid'),
    # path('list/', views.bid_list, name='bid_list'),
]