from django.conf.urls import url, include
from django.urls import path, reverse_lazy
from django.views.generic.dates import ArchiveIndexView
from django.contrib.auth import views as auth_views
from shipment import views


app_name = 'shipment'
urlpatterns = [
    path('', views.shipment_home, name='shipment-home'),
    path('shipments/', views.shipments, name='shipments'),
    path('shipments/ready-for-shipment', views.order_ready_for_shipment, name='ready-for-shipment'),
    path('shipments/detail/<uuid:shipment_uuid>/', views.shipment_detail, name='shipment-detail'),
    path('shipments/delete/<uuid:shipment_uuid>/', views.shipment_delete, name='shipment-delete'),
    path('shipments/update/<uuid:shipment_uuid>/', views.shipment_update, name='shipment-update'),
    path('ship-modes/', views.ship_modes, name='ship-modes'),
    path('ship-modes/create/', views.ship_mode_create, name='ship-mode-create'),
    path('ship-modes/detail/<uuid:ship_uuid>/', views.ship_mode_detail, name='ship-mode-detail'),
    path('ship-modes/delete/', views.ship_modes_delete, name='ship-modes-delete'),
    path('ship-modes/delete/<uuid:ship_uuid>/', views.ship_mode_delete, name='ship-mode-delete'),
    path('ship-modes/update/<uuid:ship_uuid>/', views.ship_mode_update, name='ship-mode-update'),
    path('shipments/shippeditem/<uuid:shippeditem_uuid>/', views.shippeditem_detail, name='shippeditem-detail'),
    path('histories/<uuid:shipment_uuid>/', views.shipment_history, name='shipment-history'),
    path('histories/detail/<uuid:history_uuid>/', views.shipment_history_detail, name='shipment-history-detail')
]