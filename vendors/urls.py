
from django.conf.urls import url, include
from django.urls import path, reverse_lazy
from django.views.generic.dates import ArchiveIndexView
from django.contrib.auth import views as auth_views
from vendors import views


app_name = 'vendors'
urlpatterns = [
    path('', views.vendor_home, name='vendor-home'),
    path('payments/', views.vendor_payments, name='vendor-payments'),
]