from django.conf.urls import url, include
from django.urls import path, reverse_lazy
from django.views.generic.dates import ArchiveIndexView
from django.contrib.auth import views as auth_views
from shipment import views


app_name = 'shipment'
urlpatterns = [
    path('', views.shipment_home, name='shipment-home'),
    path('shipments/', views.shipments, name='shipments'),
    path('shipments/detail/<uuid:shipment_uuid>/', views.shipment_detail, name='shipment-detail'),
    path('shipments/update/<uuid:shipment_uuid>/', views.shipment_update, name='shipment-update'),
    path('shipments/shippeditem/<uuid:shippeditem_uuid>/', views.shippeditem_detail, name='shippeditem-detail'),
    path('histories/<uuid:shipment_uuid>/', views.shipment_history, name='shipment-history'),
    path('histories/detail/<uuid:history_uuid>/', views.shipment_history_detail, name='shipment-history-detail')
]