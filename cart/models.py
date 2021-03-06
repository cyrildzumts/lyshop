from django.db import models
from django.contrib.auth.models import User
from catalog.models import Product, ProductVariant
from django.urls import reverse
from lyshop import conf
import uuid

# Create your models here.

class Coupon(models.Model):
    name = models.CharField(max_length=32, blank=False, null=False, unique=True)
    reduction = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='added_coupons', blank=False, null=False)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller_coupons', blank=True, null=True)
    activated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activated_coupons', blank=True, null=True)
    activated_at = models.DateTimeField(blank=True, null=True)
    begin_at = models.DateTimeField(blank=True, null=True)
    expire_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=False)
    usage = models.IntegerField(default=0, blank=True)
    max_usage = models.IntegerField(blank=True, null=True)
    coupon_uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return f"Coupon - {self.name} - {self.reduction}"

    def get_absolute_url(self):
        return reverse("vendors:coupon-detail", kwargs={"coupon_uuid": self.coupon_uuid})
    
    def get_dashboard_url(self):
        return reverse("dashboard:coupon-detail", kwargs={"coupon_uuid": self.coupon_uuid})
    
    def get_update_url(self):
        return reverse("dashboard:coupon-update", kwargs={"coupon_uuid": self.coupon_uuid})
    
    def get_delete_url(self):
        return reverse("dashboard:coupon-delete", kwargs={"coupon_uuid": self.coupon_uuid})

    def get_vendor_url(self):
        return reverse("vendors:coupon-detail", kwargs={"coupon_uuid": self.coupon_uuid})
    
    
    def get_vendor_update_url(self):
        return reverse("vendors:coupon-update", kwargs={"coupon_uuid": self.coupon_uuid})
    
    def get_vendor_delete_url(self):
        return reverse("vendors:coupon-delete", kwargs={"coupon_uuid": self.coupon_uuid})
    
    def get_solded_price(self, price):
        return float(price) * ((100 - self.reduction) / 100.0) 
    
    

class CartModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    #last_edited_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    amount = models.DecimalField(default=0, blank=False, null=False, max_digits=conf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=conf.PRODUCT_PRICE_DECIMAL_PLACES)
    solded_price = models.DecimalField(default=0, blank=True, null=True, max_digits=conf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=conf.PRODUCT_PRICE_DECIMAL_PLACES)
    quantity = models.IntegerField(default=0, blank=True, null=True)
    coupon = models.ForeignKey(Coupon, related_name="carts", blank=True, null=True, on_delete=models.SET_NULL)
    cart_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    FORM_FIELDS = ['user', 'amount', 'solded_price', 'coupon', 'quantity']

    def __str__(self):
        return f"Cart - {self.user.username} - {self.quantity} items"
    
    def get_absolute_url(self):
        return reverse("cart", kwargs={"cart_uuid": self.cart_uuid})
    
    def get_total(self):
        return float(self.amount) - self.get_reduction()

    def clear(self):
        pass

    def convert_to_order(self):
        pass
    

    def remove_item(self, pk):
        pass

    def update_item(self, pk, quantity):
        pass

    def get_reduction(self):
        r = 0
        if self.coupon:
            r = float(self.amount) * (self.coupon.reduction / 100.0) 
        return r
    


class CartItem(models.Model):
    cart = models.ForeignKey(CartModel, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name="cartitems")
    quantity = models.IntegerField(default=0, blank=True, null=True)
    unit_price = models.DecimalField(blank=False, null=False, max_digits=conf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=conf.PRODUCT_PRICE_DECIMAL_PLACES)
    total_price = models.DecimalField(blank=True, null=True, max_digits=conf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=conf.PRODUCT_PRICE_DECIMAL_PLACES)
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    is_active = models.BooleanField(default=True)
    item_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    FORM_FIELDS = ['cart', 'product', 'quantity', 'unit_price', 'total_price']

    def __str__(self):
        return f"CartIem - {self.product.name} - {self.quantity}"

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
    

    @property
    def is_quantity_available(self):
        return self.quantity <= self.product.quantity

    @property
    def is_product_available(self):
        return self.product.quantity > 0 and self.product.is_active
        
    @property
    def is_promoted(self):
        return self.product.is_promoted

    
    @property
    def promotion_price(self):
        return self.product.get_promotion_price

    @property
    def total_promotion_price(self):
        return self.promotion_price * self.quantity

    
    @property
    def original_price(self):
        return self.product.price

    
    @property
    def item_price(self):
        return self.product.active_price


    @property
    def item_total_price(self):
        return self.item_price * self.quantity 
    

    
    @property
    def brand(self):
        return self.product.product.brand

