from catalog import views
from django.conf.urls import url, include
from django.urls import path, reverse_lazy
from django.views.generic.dates import ArchiveIndexView
from django.contrib.auth import views as auth_views
from catalog import views


app_name = 'catalog'
urlpatterns = [
    path('', views.catalog_home, name='catalog-home'),
    path('<str:sale>/', views.catalog_home, name='sale-catalog-home'),
    path('brands/detail/<uuid:brand_uuid>/', views.brand_detail, name='brand-detail'),
    path('categories/<str:sale>/detail/<uuid:category_uuid>/', views.category_detail, name='sale-category-detail'),
    path('categories/detail/<uuid:category_uuid>/', views.category_detail, name='category-detail'),
    path('categories/products/detail/<uuid:product_uuid>/', views.product_detail, name='product-detail'),
    path('categories/products/variant/detail/<uuid:variant_uuid>/', views.product_variant_detail, name='product-variant-detail'),
    path('products/', views.ProductListView.as_view(), name='products'),
    path('products/product-image/detail/<uuid:image_uuid>/', views.product_image_detail, name='product-image-detail')
    #path('products/<uuid:product_uuid>', views.ProductDetailView.as_view(), name='product-detail'),
]