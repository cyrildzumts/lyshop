from django.conf.urls import url, include
from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from addressbook import views


app_name = 'addressbook'
urlpatterns = [
    path('', views.addressbook, name='addressbook'),
    path('addresses/', views.addresses, name='addresses'),
    path('address-details/<uuid:address_uuid>/', views.address_detail, name='address-detail'),
    path('address-delete/<uuid:address_uuid>/', views.addresse_delete, name='address-delete'),
    path('address-update/<uuid:address_uuid>/', views.address_update, name='address-update'),
    path('addresses/create/', views.address_create, name='address-create'),
    path('addresses-delete/', views.addresses_delete, name='address-delete'),
]