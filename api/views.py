from django.shortcuts import render
from django.forms.models import model_to_dict
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
    UserSerializer, AddressSerializer
 )
from accounts.models import Account
from orders.models import OrderItem, Order
from dashboard import analytics
from addressbook import addressbook_service

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

@api_view(['POST'])
def create_address(request):
    logger.info(f"API: New Address creation request from user {request.user.username}")
    if request.method != 'POST':
        return Response({'status': False, 'errror': 'Bad request. Use POST instead'}, status=status.HTTP_400_BAD_REQUEST)
    
    address = addressbook_service.create_address(request.POST.copy())
    
    if address :
        address_dict = model_to_dict(address)
        address_dict.update({'status': True})
        serialized = AddressSerializer(instance=address)
        logger.info(f"Address Dict : {address_dict}")
        logger.info(f"Address serialzed :  {serialized.data}")
        return Response(address_dict)
    
    return Response(data={'status': False, 'error': 'address not created'}, status=status.HTTP_200_OK)

@api_view(['POST'])
def update_address(request, address_uuid):
    logger.info(f"API: Address update request from user {request.user.username}")
    if request.method != 'POST':
        return Response({'status': False, 'errror': 'Bad request. Use POST instead'}, status=status.HTTP_400_BAD_REQUEST)
    
    address = addressbook_service.get_address(address_uuid)
    updated = addressbook_service.update_address(address, request.POST.copy())
    if updated :
        address.refresh_from_db()
        return Response(data={'status': True, **model_to_dict(address)}, status=status.HTTP_200_OK)
    
    return Response(data={'status': False, 'error': 'address not created'}, status=status.HTTP_200_OK)