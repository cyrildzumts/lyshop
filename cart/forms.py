from django import forms
from cart.models import CartItem
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

class AddCartForm(forms.Form):
    attr = forms.IntegerField(required=False)
    product = forms.UUIDField()
    variant_uuid = forms.UUIDField()

