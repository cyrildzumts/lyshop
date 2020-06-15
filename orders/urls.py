from django.conf.urls import url, include
from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from orders import views


app_name = 'orders'
urlpatterns = [
    path('', views.checkout, name='checkout'),
    path('checkout-success/<uuid:order_uuid>/', views.checkout_success, name='checkout-success'),
    path('checkout-failed/<uuid:order_uuid>/', views.checkout_failed, name='checkout-failed'),
]