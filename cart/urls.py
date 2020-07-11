from django.conf.urls import url, include
from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from cart import views


app_name = 'cart'
urlpatterns = [
    path('', views.cart, name='cart'),
    path('add-to-cart/', views.add_to_cart, name='cart-add'),
    path('ajax-add-coupon/', views.ajax_add_coupon, name='cart-add-coupon'),
    path('ajax-add-to-cart/', views.ajax_add_to_cart, name='cart-add-ajax'),
    path('ajax-cart-item/<uuid:item_uuid>/<str:action>/', views.ajax_cart_item_update, name='ajax-cart-item-update'),
    path('cart-update/<uuid:item_uuid>/', views.cart_update, name='cart-update'),
    path('cart-clear/', views.cart_clear, name='cart-clear'),
]