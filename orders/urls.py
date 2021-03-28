from django.conf.urls import url, include
from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from orders import views


app_name = 'orders'
urlpatterns = [
    path('', views.orders, name='order-home'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout-success/<uuid:order_uuid>/', views.checkout_success, name='checkout-success'),
    path('checkout-failed/<uuid:order_uuid>/', views.checkout_failed, name='checkout-failed'),
    path('checkout-redirect-payment/<uuid:request_uuid>/', views.checkout_redirect_payment, name='checkout-redirect-payment'),
    path('orders/', views.orders, name='orders'),
    path('order-details/<uuid:order_uuid>/', views.order_detail, name='order-detail'),
    path('order-cancel/<uuid:order_uuid>/', views.order_cancel, name='order-cancel'),
    path('download-invoice/<uuid:order_uuid>/', views.generate_invoice, name='download-invoice'),
]