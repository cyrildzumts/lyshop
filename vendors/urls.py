
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

    path('products/attributes/', views.attributes, name='attributes'),
    path('products/attributes/detail/<uuid:attribute_uuid>/', views.attribute_detail, name='attribute-detail'),
    path('products/attributes/update/<uuid:attribute_uuid>/', views.attribute_update, name='attribute-update'),
    path('products/attributes/delete/', views.delete_attributes, name='attributes-delete'),
    path('products/attributes/delete/<uuid:attribute_uuid>/', views.attribute_delete, name='attribute-delete'),
    path('products/attributes/create/<uuid:variant_uuid>/', views.attribute_create, name='attribute-create'),
    path('products/attributes/add/<uuid:variant_uuid>/', views.add_attributes, name='attribute-add'),
    path('products/attributes/remove/<uuid:variant_uuid>/', views.remove_attributes, name='attribute-remove'),

    path('products/product-images/<uuid:product_uuid>/', views.product_images, name='product-images'),
    path('products/product-image/detail/<uuid:image_uuid>/', views.product_image_detail, name='product-image-detail'),
    path('products/product-image/update/<uuid:image_uuid>/', views.product_image_update, name='product-image-update'),
    path('products/product-image/delete/<uuid:image_uuid>/', views.product_image_delete, name='product-image-delete'),
    path('products/product-image/create/<uuid:product_uuid>', views.product_image_create, name='product-image-create'),

    path('products/product-variant/detail/<uuid:variant_uuid>/', views.product_variant_detail, name='product-variant-detail'),
    path('products/product-variant/update/<uuid:variant_uuid>/', views.product_variant_update, name='product-variant-update'),
    path('products/product-variant/delete/<uuid:variant_uuid>/', views.product_variant_delete, name='product-variant-delete'),
    path('products/product-variant/create/<uuid:product_uuid>/', views.product_variant_create, name='product-variant-create'),

    path('sold-products/', views.sold_product_list, name='sold-products'),
    path('sold-products/details/<uuid:product_uuid>/', views.sold_product_detail, name='sold-product-detail'),
]