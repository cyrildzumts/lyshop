from rest_framework import viewsets
from rest_framework.permissions import BasePermission, IsAuthenticated

from api.serializers import ( 
    Account, AccountSerializer, BrandSerializer, ProductVariantSerializer, ProductSerializer, ProductAttributeSerializer,
    CategorySerializer, CartItemSerializer, OrderSerializer, OrderItemSerializer,
    UserSerializer
 )


class AccountViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AccountSerializer.Meta.model.objects.all()
    serializer_class = AccountSerializer
    #permission_classes = [IsAuthenticated]
    


class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BrandSerializer.Meta.model.objects.all()
    serializer_class = BrandSerializer
    #permission_classes = [IsAuthenticated]



class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CategorySerializer.Meta.model.objects.all()
    serializer_class = CategorySerializer
    #permission_classes = [IsAuthenticated]
    

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProductSerializer.Meta.model.objects.all()
    serializer_class = ProductSerializer


class ProductAttributeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProductAttributeSerializer.Meta.model.objects.all()
    serializer_class = ProductAttributeSerializer


class ProductVariantViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProductVariantSerializer.Meta.model.objects.all()
    serializer_class = ProductVariantSerializer

class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OrderSerializer.Meta.model.objects.all()
    serializer_class = OrderSerializer


class OrderItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OrderItemSerializer.Meta.model.objects.all()
    serializer_class = OrderItemSerializer