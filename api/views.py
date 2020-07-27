from django.shortcuts import render
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.db.models.functions import ExtractDay, ExtractMonth, ExtractYear
from django.db.models import Count, Avg, F, Q, Sum, Max, Min
from django.urls import reverse, resolve
from rest_framework import filters
from django.views.decorators.csrf import csrf_exempt
from rest_framework.generics import (
    ListCreateAPIView,
    ListAPIView,
    RetrieveUpdateDestroyAPIView
)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from api.serializers import ( 
    Account, AccountSerializer, BrandSerializer, ProductVariantSerializer, ProductSerializer, ProductAttributeSerializer,
    CategorySerializer, CartItemSerializer, OrderSerializer, OrderItemSerializer,
    UserSerializer
 )
from accounts.models import Account
from orders.models import OrderItem, Order
from dashboard import analytics

from lyshop import utils
from django.utils import timezone
from operator import itemgetter
import logging
logger = logging.getLogger(__name__)

# Create your views here.


class UserSearchByNameView(ListAPIView):
     #permission_classes = [IsAuthenticated]
     serializer_class = UserSerializer
     search_fields = ['last_name', 'first_name','username']
     filter_backends = [filters.SearchFilter]
     queryset = User.objects.filter(is_superuser=False)
     """
     def get_queryset(self):
          user_search = self.request.POST.get('user-search', "")
          if len(user_search) > 0 :
               return UserSerializer.Meta.model.objects.filter(last_name__icontains=user_search)
          return UserSerializer.Meta.model.objects.none()
     """


class UserSearchView(ListAPIView):
     #permission_classes = [IsAuthenticated]
     serializer_class = UserSerializer
     search_fields = ['last_name', 'first_name', 'username']
     filter_backends = [filters.SearchFilter]
     queryset = User.objects.filter(is_superuser=False)
     """
     def get_queryset(self):
          user_search = self.request.POST.get('user-search', "")
          if len(user_search) > 0 :
               return UserSerializer.Meta.model.objects.filter(last_name__icontains=user_search)
          return UserSerializer.Meta.model.objects.none()
     """


class BrandListView(ListAPIView):
    queryset = BrandSerializer.Meta.model.objects.all()
    serializer_class = BrandSerializer
    #permission_classes = (IsAuthenticated, )



class CategoryListView(ListAPIView):
    queryset = CategorySerializer.Meta.model.objects.all()
    serializer_class = CategorySerializer
    #permission_classes = (IsAuthenticated, )



@api_view(['GET'])
def analytics_data(request):
    logger.info(f"Report data requested by user \"{request.user.username}\"")
    response_status = status.HTTP_200_OK
    order_report = analytics.report_orders()
    order_price_report = analytics.report_orders_price()
    new_user_report = analytics.report_new_users()
    product_report = analytics.report_products()
    try:
        data = {
            'report' : order_report,
            'order_price_report' : order_price_report,
            'order_report' : order_report,
            'product_report' : product_report,
            'new_user_report' : new_user_report
        }
    except ValueError as e:
        data = {
            'errors' :  e.args
        }
        response_status = status.HTTP_400_BAD_REQUEST
    
    return Response(data, status=response_status)