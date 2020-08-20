
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
    path('payments/', views.vendor_payments, name='payments'),
    path('payments/details/<uuid:payment_uuid>/', views.payment_details, name='payment-detail'),
    path('products/', views.product_list, name='products'),
    path('product-variants/', views.product_variant_list, name='product-variants'),
    path('products/detail/<uuid:product_uuid>', views.product_list, name='product-detail'),
    path('product-variants/detail/<uuid:product_uuid>', views.product_variant_detail, name='product-variant-detail'),
    path('sold-products/', views.sold_product_list, name='sold-products'),
    path('sold-products/details/<uuid:product_uuid>/', views.sold_product_detail, name='sold-product-detail'),
]