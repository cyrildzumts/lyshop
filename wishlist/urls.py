from catalog import views
from django.conf.urls import  include
from django.urls import path, reverse_lazy
from wishlist import views


app_name = 'wishlist'
urlpatterns = [
    path('', views.wishlist_home, name='wishlist-home'),
    path('wishlists/<uuid:wishlist_uuid>/', views.wishlist, name='wishlist'),
    path('wishlists/<uuid:wishlist_uuid>/add/<uuid:product_uuid>/', views.wishlist_add, name='wishlist-item-add'),
    path('wishlists/<uuid:wishlist_uuid>/delete/<uuid:item_uuid>/', views.wishlist_remove, name='wishlist-item-delete'),
    path('wishlists/<uuid:wishlist_uuid>/clear/', views.wishlist_clear, name='wishlist-clear'),
    #path('wishlists/<uuid:wishlist_uuid>/addToCart/', views.product_variant_detail, name='wishlist-add-to-cart'),
    #path('wishlists/<uuid:wishlist_uuid>/checkout/', views.product_variant_detail, name='wishlist-checkout'),
]