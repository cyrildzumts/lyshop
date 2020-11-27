from rest_framework import serializers
from django.contrib.auth.models import User
from accounts.models import Account
from orders.models import Order, OrderItem
from catalog.models import (
    Category, Brand, Product, ProductVariant, ProductAttribute
)
from cart.models import (
    CartModel, CartItem, Coupon
)
from addressbook.models import Address


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['name', 'display_name', 'code', 'is_active']



class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'display_name','code','added_by', 'is_active', 'parent']


class ProductAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAttribute
        fields = ['name', 'display_name', 'value', 'value_type']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'display_name','added_by', 'sold_by' ,'category', 'brand', 'price', 'quantity', 'short_description','description', 'gender']

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['name', 'display_name', 'product', 'attributes', 'price', 'quantity']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["user","date_of_birth","country", "city","province","address","zip_code","telefon",
                  "newsletter","is_active_account","balance","account_type","policy","email_validated"]



class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['cart', 'product', 'quantity']



class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = Order.DEFAULT_FIELDS


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = OrderItem.DEFAULT_FIELDS


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = Address.FORM_FIELDS