from django.conf.urls import url, include
from django.urls import path, reverse_lazy
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views as drf_api_views
from api import views, viewsets

app_name = 'api'
router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('analytics/', views.analytics_data, name='analytics'),
    path('add-to-cart/', views.add_to_cart, name='add-to-cart'),
    path('current-user/', views.get_current_user, name='current-user'),
    path('update-cart-item/', views.update_cart_item, name='update-cart-item'),
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