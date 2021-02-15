from django.conf.urls import  include
from django.urls import path, reverse_lazy
from wishlist import views


app_name = 'wishlist'
urlpatterns = [
    path('', views.wishlist_home, name='wishlist-home'),
    path('wishlists/<uuid:wishlist_uuid>/', views.wishlist, name='wishlist'),
    path('wishlists/delete/<uuid:wishlist_uuid>/', views.wishlist_delete, name='wishlist-delete'),
    path('wishlists/delete/', views.wishlists_delete, name='wishlists-delete'),
    path('wishlists/create/', views.wishlist_create, name='wishlist-create'),

    path('wishlists/<uuid:wishlist_uuid>/add/<uuid:product_uuid>/', views.wishlist_add, name='wishlist-item-add'),
    path('wishlists/update/<uuid:wishlist_uuid>/', views.wishlist_update, name='wishlist-update'),
    path('wishlists/<uuid:wishlist_uuid>/delete/<uuid:item_uuid>/', views.wishlist_remove, name='wishlist-item-delete'),
    path('wishlists/<uuid:wishlist_uuid>/clear/', views.wishlist_clear, name='wishlist-clear'),
    #path('wishlists/<uuid:wishlist_uuid>/addToCart/', views.product_variant_detail, name='wishlist-add-to-cart'),
    #path('wishlists/<uuid:wishlist_uuid>/checkout/', views.product_variant_detail, name='wishlist-checkout'),
]