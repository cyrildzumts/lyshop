from django.conf.urls import url, include
from django.urls import path, reverse_lazy
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views as drf_api_views
from api import views, viewsets

app_name = 'api'
router = DefaultRouter()
router.register(r'accounts', viewsets.AccountViewSet)
router.register(r'addresses', viewsets.AddressViewSet)
router.register(r'brands', viewsets.BrandViewSet)
router.register(r'categories', viewsets.CategoryViewSet)
router.register(r'orders', viewsets.OrderViewSet)
router.register(r'products', viewsets.ProductViewSet)
router.register(r'product_variants', viewsets.ProductVariantViewSet)
router.register(r'attributes', viewsets.ProductAttributeViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('analytics/', views.analytics_data, name='analytics'),
    path('create-address/', views.create_address, name='create-address'),
    path('update-update/<uuid:address_uuid>/', views.address_update, name='update-address'),
    path('api-token-auth/', drf_api_views.obtain_auth_token, name='api-token-auth'),
    path('user-search/', views.UserSearchView.as_view(), name="user-search")
]