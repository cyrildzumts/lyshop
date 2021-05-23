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
from rest_framework.decorators import api_view, permission_classes, authentication_classes
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
from catalog import constants as CATALOG_CONSTANTS

from lyshop import utils
from django.utils import timezone
from operator import itemgetter
import logging
import uuid
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
    response_status = status.HTTP_200_OK
    order_report = analytics.report_orders()
    order_price_report = analytics.report_orders_price()
    new_user_report = analytics.report_new_users()
    product_report = analytics.report_products()
    visitor_report = analytics.report_visitors()
    try:
        data = {
            'report' : order_report,
            'order_price_report' : order_price_report,
            'order_report' : order_report,
            'product_report' : product_report,
            'new_user_report' : new_user_report,
            'visitor_report' : visitor_report
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
        logger.info(f"Address Dict : {address_dict}")
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




@api_view(['GET', 'POST'])
def client_add_payment(request, order_uuid, token):
    postdata = utils.get_postdata(request)
    
    pass


@api_view(['GET', 'POST'])
def client_add_refund(request, payment_uuid, token):
    pass


@api_view(['GET'])
def get_attribute_type(request):
    attr_template = {
    'name': _('Name'),
    'display_name': _('Display Name'),
    'value' : _('Value'),
    'is_primary' : _('Primary'),
    'value_type' : _('Value Type'),
    'value_types' : [{ 'key' :k, 'value': v } for k,v in CATALOG_CONSTANTS.ATTRIBUTE_TYPE]
    }
    return Response(data=attr_template)


@api_view(['GET','POST'])
@permission_classes([])
@authentication_classes([])
def authenticate(request):
    logger.debug("Received authenticate request")
    postdata = request.POST.copy()
    logger.debug(f"Request POST : {postdata}")
    utils.show_dict_contents(postdata, "API Athenticate Header")
    token = uuid.uuid4()
    return Response(data={"tokenType": 'Bearer', 'accessToken': token}, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([])
@authentication_classes([])
def update_activity(request):
    logger.debug("Updating User activity request")
    postdata = request.POST.copy()
    logger.debug(f"Request POST : {postdata}")
    utils.show_dict_contents(postdata, "update_activity")
    logger.debug(f"update_activity request user: {request.user}")
    return Response(data={'success': True, 'message': 'updated'}, status=status.HTTP_200_OK)