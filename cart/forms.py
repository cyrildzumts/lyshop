from django import forms
from django.core.exceptions import ValidationError
from lyshop import conf as GLOBAL_CONF
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


class CouponVerificationForm(forms.Form):
    coupon = forms.CharField(max_length=32)


class AddCartForm(forms.Form):
    attr = forms.IntegerField(required=False)
    product = forms.UUIDField()
    variant_uuid = forms.UUIDField()

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['name','seller', 'reduction', 'added_by','max_usage', 'activated_by', 'activated_at', 'is_active', 'begin_at', 'expire_at']
    
    def clean(self):
        cleaned_data = super().clean()
        expire_at = cleaned_data.get('expire_at')
        begin_at = cleaned_data.get('begin_at')
        created_at = cleaned_data.get('created_at')
        max_usage = cleaned_data.get('max_usage')
        if max_usage is not None and  (max_usage < 0 or max_usage > GLOBAL_CONF.COUPON_MAX_USAGE) :
            raise ValidationError(
                f'Invalid max usage: current max_usage = {max_usage}. max_usage must be > 0 and < {GLOBAL_CONF.COUPON_MAX_USAGE}'
            )
        if begin_at and created_at and  begin_at < created_at:
            raise ValidationError(
                f'Invalid date: begin_at({begin_at}) < created_at({created_at})'
            )

        if begin_at and expire_at and begin_at  > expire_at:
            raise ValidationError(
                f'Invalid date: begin_at({begin_at}) > expire_at({expire_at})'
            )

        
        