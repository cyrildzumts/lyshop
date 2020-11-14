from django.db import models
from django.shortcuts import reverse
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from catalog.models import Product
from orders.models import Order, OrderItem
from lyshop import conf, utils
from shipment import constants as Constants
import uuid
# Create your models here.

#TODO make this model filterable
class Shipment(models.Model):
    shipment_number = models.CharField(max_length=32, blank=True, null=True)
    shipment_ref_number = models.IntegerField(default=utils.get_random_ref)
    company = models.CharField(max_length=256, blank=True, null=True)
    customer = models.ForeignKey(User, related_name='shipment', blank=True, null=True, on_delete=models.SET_NULL)
    last_changed_by = models.ForeignKey(User, related_name='edited_shipments', blank=True, null=True, on_delete=models.SET_NULL)
    order = models.ForeignKey(Order, related_name='order_shipment', blank=True, null=True, on_delete=models.SET_NULL)
    price = models.DecimalField(blank=False, null=False, max_digits=conf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=conf.PRODUCT_PRICE_DECIMAL_PLACES)
    created_at = models.DateTimeField(auto_now_add=True)
    last_changed_at = models.DateTimeField(auto_now=True)
    shipped_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    shipment_status = models.IntegerField(default=Constants.WAITING, blank=True)
    shipment_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    DEFAULT_UPDATE_FIELDS = ['company', 'shipped_at', 'delivered_at', 'shipment_status']

    def __str__(self):
        return f"Shipment {self.shipment_number}"

    def get_absolute_url(self):
        return reverse("shipment:shipment-detail", kwargs={"shipment_uuid": self.shipment_uuid})

    def get_delete_url(self):
        return reverse("shipment:shipment-delete", kwargs={"shipment_uuid": self.shipment_uuid})
    
    def get_update_url(self):
        return reverse("shipment:shipment-update", kwargs={"shipment_uuid": self.shipment_uuid})
    
    def get_history_url(self):
        return reverse("shipment:shipment-history", kwargs={"shipment_uuid": self.shipment_uuid})


class ShippedItem(models.Model):
    product = models.ForeignKey(Product, related_name="shippeditem", on_delete=models.SET_NULL, blank=True, null=True)
    order_item = models.ForeignKey(OrderItem, related_name="shippeditem", on_delete=models.SET_NULL, blank=True, null=True)
    shipment = models.ForeignKey(Shipment, related_name="shippeditems", blank=False, null=False, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField( max_digits=conf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=conf.PRODUCT_PRICE_DECIMAL_PLACES)
    total_price = models.DecimalField( max_digits=conf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=conf.PRODUCT_PRICE_DECIMAL_PLACES)
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    shippeditem_uuid = models.UUIDField(default=uuid.uuid4, editable=False)


    def __str__(self):
        return f"ShippedItem {self.product.display_name}"

    def get_absolute_url(self):
        return reverse("shipment:shippedItem-detail", kwargs={"shippeditem_uuid": self.shippeditem_uuid})


class ShipmentStatusHistory(models.Model):
    shipment_status = models.IntegerField(default=Constants.WAITING)
    shipment_ref_id = models.IntegerField(blank=False, null=False)
    changed_by = models.ForeignKey(User, related_name='shipment_edit_histories', blank=True, null=True, on_delete=models.SET_NULL)
    shipment = models.ForeignKey(Shipment, related_name="shipment_status_history", blank=True, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    history_uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    def get_absolute_url(self):
       return reverse('shipment:shipment-history-detail', kwargs={'history_uuid':self.history_uuid})

    def get_dashboard_url(self):
        return reverse('dashboard:shipment-history-detail', kwargs={'history_uuid':self.history_uuid})
