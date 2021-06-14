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
    path('add-to-cart/', views.add_to_cart, name='add-to-cart'),
    path('update-cart-item/<uuid:item_uuid>/<str:action>/', views.update_cart_item, name='update-cart-item'),
    path('verify-coupon/', views.verify_coupon, name='verify-coupon'),
    path('remove-coupon/', views.remove_coupon_from_cart, name='remove-coupon'),
    path('authenticate/', views.authenticate, name='authenticate'),
    path('create-address/', views.create_address, name='create-address'),
    path('attribute-types/', views.get_attribute_type, name='attribute-types'),
    path('update-activity/', views.update_activity, name='update-activity'),
    path('update-address/<uuid:address_uuid>/', views.update_address, name='update-address'),
    path('api-token-auth/', drf_api_views.obtain_auth_token, name='api-token-auth'),
    path('user-search/', views.UserSearchView.as_view(), name="user-search"),
]