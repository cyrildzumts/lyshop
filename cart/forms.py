from django import forms
from cart.models import CartItem, Coupon
from catalog.models import Product, ProductVariant




class CartItemForm(forms.ModelForm):
    
    class Meta:
        model = CartItem
        fields = ['cart', 'product', 'quantity']

class AddToCartForm(forms.ModelForm):

    class Meta:
        model = CartItem
        fields = ['product', 'quantity']

class CartItemUpdateForm(forms.ModelForm):

    class Meta:
        model = CartItem
        fields = ['product', 'quantity']

class CartItemQuantityUpdateForm(forms.Form):
    item_uuid = forms.UUIDField()
    quantity = forms.IntegerField()



class AddCartForm(forms.Form):
    attr = forms.IntegerField(required=False)
    product = forms.UUIDField()
    variant_uuid = forms.UUIDField()

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['name', 'reduction', 'added_by', 'activated_by', 'activated_at', 'is_active', 'expire_at']