
from django import forms
from orders.models import PaymentRequest, Order, OrderItem, PaymentMethod, OrderPayment, Refund
from core.forms import ListField, IntergerListField



class PaymentRequestForm(forms.ModelForm):
    
    class Meta:
        model = PaymentRequest
        fields = ['token','pay_url', 'verification_code', 'order', 'amount', 'unit_price','quantity', 'tva', 'commission',
        'country', 'status', 'product_name','customer', 'customer_name', 'description'
        ]

class ShippingAddressForm(forms.Form):

    user = forms.IntegerField()
    shipping_firstname = forms.CharField(max_length=32)
    shipping_lastname = forms.CharField(max_length=32)
    shipping_city = forms.CharField(max_length=32)
    shipping_country = forms.CharField(max_length=32)
    shipping_address_extra = forms.CharField(max_length=32, required=False)
    shipping_postal_code = forms.IntegerField()
    shipping_street = forms.CharField(max_length=32, required=False)
    shipping_house_number = forms.IntegerField(required=False)
    billing_shipping = forms.BooleanField()


class BillingAddressForm(forms.Form):

    user = forms.IntegerField()
    billing_firstname = forms.CharField(max_length=32)
    billing_lastname = forms.CharField(max_length=32)
    billing_city = forms.CharField(max_length=32)
    billing_country = forms.CharField(max_length=32)
    billing_address_extra = forms.CharField(max_length=32, required=False)
    billing_postal_code = forms.IntegerField()
    billing_street = forms.CharField(max_length=32, required=False)
    billing_house_number = forms.IntegerField(required=False)


class PaymentOptionForm(forms.Form):
    payment_option = forms.IntegerField()


class PaymentMethodForm(forms.ModelForm):
    class Meta:
        model = PaymentMethod
        fields = PaymentMethod.FORM_FIELDS


class DashboardOrderUpdateForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ['last_changed_by', 'status', 'is_paid']



class OrderFilterOption(forms.Form):
    order_status = IntergerListField(coerce=int, required=False)
    #order_status = forms.IntegerField(required=False)
    payment_option = forms.IntegerField(required=False)
    amount = forms.IntegerField(required=False)
    date = forms.DateTimeField(required=False)


class OrderItemUpdateForm(forms.ModelForm):

    class Meta:
        model = OrderItem
        fields = ['changed_by', 'quantity']


class RefundForm(forms.ModelForm):

    class Meta:
        model = Refund
        fields = Refund.FORM_FIELDS