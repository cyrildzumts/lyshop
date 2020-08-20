
from django.conf.urls import url, include
from django.urls import path, reverse_lazy
from django.views.generic.dates import ArchiveIndexView
from django.contrib.auth import views as auth_views
from vendors import views


app_name = 'vendors'
urlpatterns = [
    path('', views.vendor_home, name='vendor-home'),
    path('balance-history/<uuid:balance_uuid>/', views.balance_history, name='balance-history'),
    path('balance-history/details/<uuid:history_uuid>/', views.balance_history_detail, name='balance-history-detail'),
    path('payments/', views.vendor_payments, name='vendor-payments'),
    path('payments/details/<uuid:payment_uuid>/', views.payment_details, name='payment-detail'),
    path('sold-products/', views.product_list, name='vendor-sold-products'),
]