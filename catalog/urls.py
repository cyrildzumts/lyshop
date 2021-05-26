from catalog import views
from django.conf.urls import url, include
from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from catalog import views


app_name = 'catalog'
catalog_patterns = [
    path('', views.catalog_home, name='catalog-home'),
    path('categories/detail/<uuid:category_uuid>/', views.category_detail, name='category-detail'),
    path('categories/<slug:slug>/', views.category_detail_slug, name='category-detail-slug'),
    path('categories/products/detail/<uuid:product_uuid>/', views.product_detail, name='product-detail'),
    path('categories/products/variant/detail/<uuid:variant_uuid>/', views.product_variant_detail, name='product-variant-detail'),
    path('products/', views.ProductListView.as_view(), name='products'),
    path('products/product-image/detail/<uuid:image_uuid>/', views.product_image_detail, name='product-image-detail')
]

urlpatterns = [
    path('', include(catalog_patterns)),
    path('<str:sale>/', include((catalog_patterns,app_name), namespace='sale')),
    path('brands/detail/<uuid:brand_uuid>/', views.brand_detail, name='brand-detail'),
    
    #path('products/<uuid:product_uuid>', views.ProductDetailView.as_view(), name='product-detail'),
]