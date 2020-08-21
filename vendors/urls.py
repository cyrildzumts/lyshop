
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
    path('products/detail/<uuid:product_uuid>/', views.product_detail, name='product-detail'),
    path('products/update/<uuid:product_uuid>/', views.product_update, name='product-update'),
    path('products/delete/<uuid:product_uuid>/', views.product_delete, name='product-delete'),
    path('products/delete/', views.products_delete, name='products-delete'),
    path('products/create/', views.product_create, name='product-create'),

    path('products/product-variant/detail/<uuid:variant_uuid>/', views.product_variant_detail, name='product-variant-detail'),
    path('products/product-variant/update/<uuid:variant_uuid>/', views.product_variant_update, name='product-variant-update'),
    path('products/product-variant/delete/<uuid:variant_uuid>/', views.product_variant_delete, name='product-variant-delete'),
    path('products/product-variant/create/<uuid:product_uuid>/', views.product_variant_create, name='product-variant-create'),

    path('sold-products/', views.sold_product_list, name='sold-products'),
    path('sold-products/details/<uuid:product_uuid>/', views.sold_product_detail, name='sold-product-detail'),
]