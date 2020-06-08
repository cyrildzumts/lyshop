from django.db import models
from django.shortcuts import reverse
from django.contrib.auth.models import User
from catalog.models import ProductVariant
from catalog import conf
import uuid

# Create your models here.

PR_ACTIVE           = 'Active'
PR_CANCELED         = 'Canceled'
PR_CLEARED          = 'Cleared'
PR_ACCEPTED         = 'Accepted'
PR_CREATED          = 'Created'
PR_COMPLETED        = 'Completed'
PR_DECLINED         = 'Declined'
PR_EXPIRED          = 'Expired'
PR_FAILED           = 'Failed'
PR_PAID             = 'Paid'
PR_PROCESSED        = 'Processed'
PR_PENDING          = 'Pending'
PR_REFUSED          = 'Refused'
PR_REVERSED         = 'Reversed'

PR_STATUS = [
    PR_ACCEPTED,PR_ACTIVE, PR_CANCELED, PR_CLEARED,
    PR_COMPLETED, PR_CREATED, PR_DECLINED, PR_EXPIRED,
    PR_FAILED, PR_PAID, PR_PENDING, PR_PROCESSED, 
    PR_REFUSED, PR_REVERSED
]


ORDER_SUBMITTED = 0
ORDER_PROCESSING = 1
ORDER_PAID = 2
ORDER_CANCELED = 3
ORDER_SHIPPED = 4
ORDER_DELIVERED = 5
ORDER_PICKED_UP = 6
ORDER_NOT_PICKED_UP = 7


ORDER_STATUS = (
    (ORDER_SUBMITTED, 'Submitted'),
    (ORDER_PROCESSING, 'Processing'),
    (ORDER_PAID, 'Paid'),
    (ORDER_CANCELED, 'Canceled'),
    (ORDER_SHIPPED, 'Shipped'),
    (ORDER_DELIVERED, 'Delivered'),
    (ORDER_PICKED_UP, 'Picked up'),
    (ORDER_NOT_PICKED_UP, 'Not picked  up'),
)

PAY_AT_DELIVERY = 0
PAY_AT_ORDER = 1

PAYMENT_OPTIONS = (
    (PAY_AT_DELIVERY, 'Pay at delivery'),
    (PAY_AT_ORDER, 'Pay at order'),
)


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
    last_edited_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    amount = models.DecimalField(default=0, blank=False, null=False, max_digits=conf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=conf.PRODUCT_PRICE_DECIMAL_PLACES)
    quantity = models.IntegerField(default=0, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    is_active = models.BooleanField(default=True, blank=True, null=True)
    is_closed = models.BooleanField(default=False, blank=True, null=True)
    status = models.IntegerField(default=ORDER_SUBMITTED)
    payment_option = models.IntegerField(default=PAY_AT_ORDER)
    order_uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return f'Order {self.user.username}'
    
    def get_absolute_url(self):
        return reverse("orders:order-detail", kwargs={"order_uuid": self.order_uuid})
    
    def get_dashboard_url(self):
        return reverse("dashboard:order-detail", kwargs={"order_uuid": self.order_uuid})
    
    def get_update_url(self):
        return reverse("dashboard:order-update", kwargs={"order_uuid": self.order_uuid})
    
    def get_delete_url(self):
        return reverse("dashboard:order-delete", kwargs={"order_uuid": self.order_uuid})
    


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)
    product = models.OneToOneField(ProductVariant, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField( max_digits=conf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=conf.PRODUCT_PRICE_DECIMAL_PLACES)
    total_price = models.DecimalField( max_digits=conf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=conf.PRODUCT_PRICE_DECIMAL_PLACES)
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    is_active = models.BooleanField(default=True, blank=True, null=True)
    item_uuid = models.UUIDField(default=uuid.uuid4, editable=False)

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
    token = models.CharField(max_length=32, blank=True, null=True)
    verification_code = models.TextField(max_length=80, blank=True, null=True)
    seller = models.ForeignKey(User, on_delete=models.CASCADE ,blank=False )
    amount = models.DecimalField( max_digits=conf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=conf.PRODUCT_PRICE_DECIMAL_PLACES)
    unit_price = models.DecimalField( max_digits=conf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=conf.PRODUCT_PRICE_DECIMAL_PLACES, blank=True, null=True)
    quantity = models.IntegerField(default=1, blank=True, null=True)
    tva = models.DecimalField( max_digits=conf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=conf.PRODUCT_PRICE_DECIMAL_PLACES, blank=True, null=True)
    commission =  models.DecimalField( max_digits=conf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=conf.PRODUCT_PRICE_DECIMAL_PLACES, blank=True, null=True)
    country = models.CharField(max_length=32, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(default=PR_CREATED,max_length=32, blank=False, null=False)
    product_name = models.CharField(max_length=255 ,blank=False, null=False)
    customer_name = models.CharField(max_length=255 ,blank=False, null=False)
    description = models.CharField(max_length=255 ,blank=False, null=False)
    