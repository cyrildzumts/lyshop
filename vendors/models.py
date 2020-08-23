from django.db import models
from django.db.models import Q
from django.shortcuts import reverse
from django.contrib.auth.models import User, Group
from lyshop import conf
import uuid

# Create your models here.

class Balance(models.Model):
    name = models.CharField(max_length=64)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, blank=True, null=True)
    balance = models.DecimalField(blank=False, null=False, max_digits=conf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=conf.PRODUCT_PRICE_DECIMAL_PLACES)
    balance_uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("vendors:balance-detail", kwargs={"balance_uuid": self.balance_uuid})
    
    def get_history_url(self):
        return reverse('vendors:balance-history', kwargs={'balance_uuid':self.balance_uuid})

class BalanceHistory(models.Model):
    balance_ref_id = models.IntegerField(blank=False, null=False)
    balance_amount = models.DecimalField(blank=False, null=False, max_digits=conf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=conf.PRODUCT_PRICE_DECIMAL_PLACES)
    sender = models.ForeignKey(User, related_name='sender_histories', blank=True, null=True, on_delete=models.SET_NULL)
    receiver = models.ForeignKey(User, related_name='receiver_histories', blank=True, null=True, on_delete=models.SET_NULL)
    balance = models.ForeignKey(Balance, related_name="balance_history", blank=True, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    history_uuid = models.UUIDField(default=uuid.uuid4, editable=False)    


    def __str__(self):
        return f"BalanceHistory {self.id}"

    def get_absolute_url(self):
        return reverse("vendors:balance-history-detail", kwargs={"history_uuid": self.history_uuid})
    

class VendorPayment(models.Model):
    seller = models.ForeignKey(User, related_name='vendorpayments', blank=False, null=True, on_delete=models.SET_NULL)
    amount = models.DecimalField(blank=False, null=False, max_digits=conf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=conf.PRODUCT_PRICE_DECIMAL_PLACES)
    balance_amount = models.DecimalField(blank=False, null=False, max_digits=conf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=conf.PRODUCT_PRICE_DECIMAL_PLACES)
    pay_username = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    payment_uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return f"VendorPayment {self.id}"

    def get_absolute_url(self):
        return reverse("vendors:payment-detail", kwargs={"payment_uuid": self.payment_uuid})


class VendorPaymentHistory(models.Model):
    payment_ref_id = models.IntegerField(blank=False, null=False)
    amount = models.DecimalField(blank=False, null=False, max_digits=conf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=conf.PRODUCT_PRICE_DECIMAL_PLACES)
    payment = models.ForeignKey(VendorPayment, related_name="payment_history", blank=True, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    history_uuid = models.UUIDField(default=uuid.uuid4, editable=False)    


    def __str__(self):
        return f"VendorPaymentHistory {self.id}"


class SoldProduct(models.Model):
    seller = models.ForeignKey(User, related_name='vendor_sold_products', blank=False, null=True, on_delete=models.SET_NULL)
    customer = models.ForeignKey(User, related_name='customer_bought_products', blank=False, null=True, on_delete=models.SET_NULL)
    product = models.ForeignKey('catalog.ProductVariant', blank=False, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    product_uuid = models.UUIDField(default=uuid.uuid4, editable=False)  

    def __str__(self):
        return f"SoldProduct {self.product.name}"

    def get_absolute_url(self):
        return reverse("vendors:sold-product-detail", kwargs={"product_uuid": self.product_uuid})
    
    def get_dashboard_url(self):
        return reverse("vendors:sold-product-detail", kwargs={"product_uuid": self.product_uuid})

    def get_vendor_url(self):
        return reverse("vendors:sold-product-detail", kwargs={"product_uuid": self.product_uuid})
