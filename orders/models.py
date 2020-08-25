from django.db import models
from django.db.models import Q
from django.shortcuts import reverse
from django.contrib.auth.models import User
from catalog.models import ProductVariant
from lyshop import conf
from orders import commons
from lyshop import settings, utils
import uuid

# Create your models here.


class Address(models.Model):
    user = models.ForeignKey(User, related_name='addresses', blank=True, null=True, on_delete=models.SET_NULL)
    city = models.CharField(max_length=32)
    country = models.CharField(max_length=32)
    postal_code = models.IntegerField(blank=True, null=True)
    address_extra = models.CharField(max_length=32, blank=True, null=True)
    street = models.CharField(max_length=32, blank=True, null=True)
    house_number = models.IntegerField(blank=True, null=True)
    address_uuid = models.UUIDField(default=uuid.uuid4, editable=False)



class Order(models.Model):
    user = models.ForeignKey(User, related_name='orders', blank=True, null=True, on_delete=models.SET_NULL)
    order_ref_number = models.IntegerField(default=utils.get_random_ref)
    last_edited_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    last_changed_by = models.ForeignKey(User, related_name='edited_orders', blank=True, null=True, on_delete=models.SET_NULL)
    amount = models.DecimalField(default=0, blank=False, null=False, max_digits=conf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=conf.PRODUCT_PRICE_DECIMAL_PLACES)
    shipping_price = models.DecimalField(default=0, blank=True, null=True, max_digits=conf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=conf.PRODUCT_PRICE_DECIMAL_PLACES)
    solded_price = models.DecimalField(default=0, blank=True, null=True, max_digits=conf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=conf.PRODUCT_PRICE_DECIMAL_PLACES)
    total = models.DecimalField(default=0, blank=False, null=False, max_digits=conf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=conf.PRODUCT_PRICE_DECIMAL_PLACES)
    quantity = models.IntegerField(default=0, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    is_active = models.BooleanField(default=True, blank=True, null=True)
    is_closed = models.BooleanField(default=False, blank=True, null=True)
    is_paid = models.BooleanField(default=False, blank=True)
    vendor_balance_updated = models.BooleanField(default=False, blank=True)
    status = models.IntegerField(default=commons.ORDER_SUBMITTED)
    payment_option = models.IntegerField(default=commons.PAY_AT_ORDER)
    coupon = models.ForeignKey("cart.Coupon", related_name="orders", blank=True, null=True, on_delete=models.SET_NULL)
    order_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    DEFAULT_FIELDS = ['user', 'amount', 'quantity', 'created_at', 'status', 'coupon', 'payment_option', 'total', 'shipping_price', 'is_closed', 'solded_price', 'order_uuid']
    
    def __str__(self):
        return f'Order {self.user.username}'
    
    def get_absolute_url(self):
        return reverse("orders:order-detail", kwargs={"order_uuid": self.order_uuid})
    
    def get_dashboard_url(self):
        return reverse("dashboard:order-detail", kwargs={"order_uuid": self.order_uuid})
    
    def get_update_url(self):
        return reverse("dashboard:order-update", kwargs={"order_uuid": self.order_uuid})
    
    def get_history_url(self):
        return reverse("dashboard:order-history", kwargs={"order_uuid": self.order_uuid})
    
    def get_delete_url(self):
        return reverse("dashboard:order-delete", kwargs={"order_uuid": self.order_uuid})
    
    def get_reduction(self):
        r = 0
        if self.coupon:
            r = float(self.amount) * (self.coupon.reduction / 100.0) 
        return r

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)
    product = models.ForeignKey(ProductVariant, related_name='order_items', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField( max_digits=conf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=conf.PRODUCT_PRICE_DECIMAL_PLACES)
    total_price = models.DecimalField( max_digits=conf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=conf.PRODUCT_PRICE_DECIMAL_PLACES)
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    is_active = models.BooleanField(default=True, blank=True, null=True)
    item_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    DEFAULT_FIELDS = ['order', 'product', 'quantity', 'unit_price', 'total_price','created_at', 'item_uuid']

    def __str__(self):
        return f"OrderIem - {self.product.name} - {self.quantity}"

    def get_image_url(self):
        if self.product.images.exists():
            return self.product.images.first().get_image_url()
        elif self.product.product.images.exists():
            return self.product.product.images.first().get_image_url()
    
    @property
    def display_name(self):
        return self.product.display_name
    
    @property
    def name(self):
        return self.product.name


class PaymentRequest(models.Model):
    token = models.CharField(max_length=128, blank=True, null=True)
    pay_url = models.TextField(max_length=256, blank=False, null=False)
    verification_code = models.TextField(max_length=80, blank=True, null=True)
    order = models.ForeignKey(Order, related_name='payment_requests', on_delete=models.CASCADE, blank=True, null=True)
    customer = models.ForeignKey(User, on_delete=models.CASCADE ,blank=False )
    amount = models.DecimalField( max_digits=conf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=conf.PRODUCT_PRICE_DECIMAL_PLACES)
    unit_price = models.DecimalField( max_digits=conf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=conf.PRODUCT_PRICE_DECIMAL_PLACES, blank=True, null=True)
    quantity = models.IntegerField(default=1, blank=True, null=True)
    tva = models.DecimalField( max_digits=conf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=conf.PRODUCT_PRICE_DECIMAL_PLACES, blank=True, null=True)
    commission =  models.DecimalField( max_digits=conf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=conf.PRODUCT_PRICE_DECIMAL_PLACES, blank=True, null=True)
    country = models.CharField(max_length=128, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(default=commons.PR_CREATED,max_length=32, blank=False, null=False)
    payment_status = models.IntegerField(default=commons.PAYMENT_CREATED, blank=True, null=True)
    product_name = models.CharField(max_length=255 ,blank=False, null=False)
    requester_name = models.CharField(max_length=255 ,blank=False, null=False, default=settings.PAY_USERNAME)
    customer_name = models.CharField(max_length=255 ,blank=False, null=False)
    description = models.CharField(max_length=255 ,blank=False, null=False)
    redirect_success_url = models.TextField(max_length=256, blank=True, null=True)
    redirect_failed_url = models.TextField(max_length=256, blank=True, null=True)
    failed_reason = models.TextField(max_length=256, blank=True, null=True)
    request_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    DEFAULT_FIELDS = ['token', 'pay_url', 'verification_code', 'order', 'customer', 'amount', 'created_at', 'status', 'request_uuid']


    def __str__(self):
        return "Payment Request id : {0} - Amount : {1}".format(self.pk, self.amount)
    
    def get_absolute_url(self):
       return reverse('payments:payment-detail', kwargs={'request_uuid':self.request_uuid})

    def get_dashboard_url(self):
        return reverse('dashboard:payment-request-detail', kwargs={'request_uuid':self.request_uuid})

    @staticmethod
    def get_user_payments(user):
        queryset = PaymentRequest.objects.none()
        if user and user.is_authenticated:
            queryset = PaymentRequest.objects.filter(order__user=user)
        return queryset


class OrderStatusHistory(models.Model):
    order_status = models.IntegerField()
    order_ref_id = models.IntegerField(blank=False, null=False)
    order = models.ForeignKey(Order, related_name="order_status_history", blank=True, null=True, on_delete=models.SET_NULL)
    changed_by = models.ForeignKey(User, related_name='order_edit_histories', blank=True, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    history_uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    def get_absolute_url(self):
       return reverse('orders:history-detail', kwargs={'history_uuid':self.history_uuid})

    def get_dashboard_url(self):
        return reverse('dashboard:order-history-detail', kwargs={'history_uuid':self.history_uuid})
