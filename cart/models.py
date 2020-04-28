from django.db import models
from django.contrib.auth.models import User
from catalog.models import Product, ProductVariant
from django.urls import reverse
from catalog import conf
import uuid

# Create your models here.

class CartModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    #last_edited_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    amount = models.DecimalField(default=0, blank=False, null=False, max_digits=conf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=conf.PRODUCT_PRICE_DECIMAL_PLACES)
    quantity = models.IntegerField(default=0, blank=True, null=True)
    cart_uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return f"Cart - {self.user.username} - {self.quantity} items"
    


    def get_absolute_url(self):
        return reverse("cart", kwargs={"cart_uuid": self.cart_uuid})
    
    def get_total(self):
        pass

    def clear(self):
        pass

    def convert_to_order(self):
        pass
    

    def remove_item(self, pk):
        pass

    def update_item(self, pk, quantity):
        pass





class CartItem(models.Model):
    cart = models.ForeignKey(CartModel, on_delete=models.CASCADE, related_name='items')
    product = models.OneToOneField(ProductVariant, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0, blank=True, null=True)
    unit_price = models.DecimalField(blank=False, null=False, max_digits=conf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=conf.PRODUCT_PRICE_DECIMAL_PLACES)
    total_price = models.DecimalField(blank=True, null=True, max_digits=conf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=conf.PRODUCT_PRICE_DECIMAL_PLACES)
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    is_active = models.BooleanField(default=True, blank=True, null=True)
    item_uuid = models.UUIDField(default=uuid.uuid4, editable=False)

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
    def brand(self):
        return self.product.product.brand

