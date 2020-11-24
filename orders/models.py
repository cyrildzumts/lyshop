from django.db import models
from django.db.models import Q, UniqueConstraint
from django.shortcuts import reverse
from django.contrib.auth.models import User
from catalog.models import ProductVariant
from addressbook.models import Address
from lyshop import conf
from orders import commons
from lyshop import settings, utils
import uuid

# Create your models here.

class Order(models.Model):
    user = models.ForeignKey(User, related_name='orders', blank=True, null=True, on_delete=models.SET_NULL)
    order_ref_number = models.IntegerField(default=utils.get_random_ref)
    last_edited_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    last_changed_by = models.ForeignKey(User, related_name='edited_orders', blank=True, null=True, on_delete=models.SET_NULL)
    amount = models.DecimalField(default=0, blank=False, null=False, max_digits=conf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=conf.PRODUCT_PRICE_DECIMAL_PLACES)
    shipping_price = models.DecimalField(default=0, blank=True, null=True, max_digits=conf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=conf.PRODUCT_PRICE_DECIMAL_PLACES)
    solded_price = models.DecimalField(blank=True, null=True, max_digits=conf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=conf.PRODUCT_PRICE_DECIMAL_PLACES)
    total = models.DecimalField(default=0, blank=False, null=False, max_digits=conf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=conf.PRODUCT_PRICE_DECIMAL_PLACES)
    quantity = models.IntegerField(default=0, blank=True, null=True)
    address = models.ForeignKey('addressbook.Address', blank=True, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    is_active = models.BooleanField(default=True, blank=True, null=True)
    is_closed = models.BooleanField(default=False, blank=True, null=True)
    is_paid = models.BooleanField(default=False, blank=True)
    vendor_balance_updated = models.BooleanField(default=False, blank=True)
    status = models.IntegerField(default=commons.ORDER_SUBMITTED)
    payment_option = models.IntegerField(default=commons.PAY_WITH_PAY)
    coupon = models.ForeignKey("cart.Coupon", related_name="orders", blank=True, null=True, on_delete=models.SET_NULL)
    order_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    DEFAULT_FIELDS = ['user', 'amount', 'quantity', 'created_at', 'status', 'coupon', 'payment_option', 'total', 'shipping_price', 'is_closed', 'solded_price', 'order_uuid']
    FILTERABLE_FIELDS = ['amount','created_at', 'payment_option', 'status']
    FILTER_CONFIG = {
        'model' : 'Order',
        'fields' : FILTERABLE_FIELDS,
        'amount' : {'field_name': 'amount','display_name': 'Amount', 'template_name' : 'tags/decimal_field.html', 'range': True, 'selection' : False, 'selection_options' : ()},
        'created_at' : {'field_name': 'created_at','display_name': 'Creation Date', 'template_name' : 'tags/datetime_field.html', 'range': True, 'selection' : False, 'selection_options' : ()},
        'payment_option' : {'field_name': 'payment_option','display_name': 'Payment Option', 'template_name' : 'tags/integer_field.html','range': False, 'selection' : True, 'selection_options' : commons.PAYMENT_OPTIONS},
        'status' : {'field_name': 'status','display_name': 'Status', 'template_name' : 'tags/integer_field.html', 'range': False, 'selection' : True, 'selection_options' : commons.ORDER_STATUS},
    }


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

    @property
    def total_price(self):
        return (self.solded_price or self.amount) + self.shipping_price

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)
    last_edited_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    changed_by = models.ForeignKey(User, related_name='changed_orderitems', blank=True, null=True, on_delete=models.SET_NULL)
    product = models.ForeignKey(ProductVariant, related_name='order_items', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField( max_digits=conf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=conf.PRODUCT_PRICE_DECIMAL_PLACES)
    promotion_price = models.DecimalField(blank=True, null=True, max_digits=conf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=conf.PRODUCT_PRICE_DECIMAL_PLACES)
    total_price = models.DecimalField( max_digits=conf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=conf.PRODUCT_PRICE_DECIMAL_PLACES)
    total_promotion_price = models.DecimalField(blank=True, null=True, max_digits=conf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=conf.PRODUCT_PRICE_DECIMAL_PLACES)
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
    
    def get_absolute_url(self):
        return reverse("orders:order-item", kwargs={"order_uuid": self.order.order_uuid, "item_uuid": self.item_uuid})
    
    def get_dashboard_url(self):
        return reverse("dashboard:order-item", kwargs={"order_uuid": self.order.order_uuid, "item_uuid": self.item_uuid})
    
    def get_update_url(self):
        return reverse("dashboard:order-item-update", kwargs={"order_uuid": self.order.order_uuid, "item_uuid": self.item_uuid})

    def get_vendor_url(self):
        return reverse("vendors:order-item", kwargs={"order_uuid": self.order.order_uuid, "item_uuid": self.item_uuid})
    
    def get_vendor_update_url(self):
        return reverse("vendors:order-item-update", kwargs={"order_uuid": self.order.order_uuid, "item_uuid": self.item_uuid})

    @property
    def image(self):
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

    @property
    def brand(self):
        return self.product.product.brand

    @property
    def gender(self):
        return self.product.product.gender
    
    @property
    def was_promoted(self):
        return self.promotion_price is not None

    @property
    def total_promoton_price(self):
        if self.was_promoted:
            return  self.quantity * self.promotion_price
        return 0
    
    @property
    def active_total_price(self):
        return (self.promotion_price or self.unit_price) * self.quantity


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


class PaymentMethod(models.Model):
    name = models.CharField(max_length=255 ,blank=False, null=False)
    display_name = models.CharField(max_length=255 ,blank=False, null=False)
    provider = models.CharField(max_length=255 ,blank=False, null=False)
    credential = models.CharField(max_length=255 ,blank=False, null=False)
    is_active = models.BooleanField(default=False, blank=True, null=True)
    mode = models.IntegerField(default=commons.ORDER_PAYMENT_PAY, blank=True, null=True, choices=commons.ORDER_PAYMENT_MODE)
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    changed_by = models.ForeignKey(User, related_name='changed_payment_methods', blank=True, null=True, on_delete=models.SET_NULL)
    added_by = models.ForeignKey(User, related_name='added_payment_methods', blank=True, null=True, on_delete=models.SET_NULL)
    method_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    FORM_FIELDS = ['name', 'display_name', 'provider', 'credential', 'mode', 'is_active', 'added_by', 'changed_by']

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['provider', 'credential', 'mode'], name='unique_payment_method'),
            models.UniqueConstraint(fields=['name', 'display_name'], name='unique_payment_method_naming'),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.display_name}"

    def get_absolute_url(self):
       return reverse('dashbord:payment-method-detail', kwargs={'method_uuid':self.method_uuid})

    def get_dashboard_url(self):
        return reverse('dashboard:payment-method-detail', kwargs={'method_uuid':self.method_uuid})
    
    def get_delete_url(self):
        return reverse('dashboard:payment-method-delete', kwargs={'method_uuid':self.method_uuid})
    
    def get_update_url(self):
        return reverse('dashboard:payment-method-update', kwargs={'method_uuid':self.method_uuid})
    
