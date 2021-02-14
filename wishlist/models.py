from django.db import models
from django.contrib.auth.models import User
from wishlist import constants
import uuid
# Create your models here.

class Wishlist(models.Model):
    name = models.CharField(max_length=64)
    customer = models.ForeignKey(User, related_name=constants.USER_RELATED_NAME, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    wishlist_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    FORM_FIELDS = ['name', 'customer']

    class Meta:
        ordering = constants.ORDERING

    def __str__(self):
        return f"Wishlist -{self.name} - {self.customer.get_full_name()}"

    def get_absolute_url(self):
        return reverse("wishlist:wishlist", kwargs={"wishlist_uuid": self.wishlist_uuid})

    def get_clear_url(self):
        return reverse("wishlist:wishlist-clear", kwargs={"wishlist_uuid": self.wishlist_uuid})

    def get_dashboard_url(self):
        pass
        #return reverse("dashboard:wishlist", kwargs={"wishlist_uuid": self.wishlist_uuid})
    



class WishlistItem(models.Model):
    wishlists = models.ManyToManyField(Wishlist, related_name=constants.WISHLIST_MANY_TO_MANY_RELATED_NAME)
    product = models.ForeignKey(constants.WISHLIST_ITEM_FOREIGN_KEY, related_name=constants.WISHLIST_ITEM_RELATED_NAME, on_delete=models.CASCADE)


    def __str__(self):
        return f"WishlistItem - {self.product.display_name}"
    

    @property
    def name(self):
        """
        Return the name of the associated Product
        """
        return self.product.name
    

    @property
    def display_name(self):
        """
        Return the name of the associated Product
        """
        return self.product.display_name
    
    @property
    def price(self):
        """
        Return the price of the associated Product
        """
        return self.product.price
    
    @property
    def promotion_price(self):
        """
        Return the price of the associated Product
        """
        return self.product.promotion_price

    def get_absolute_url(self):
        """
        Return the URL of the associated Product
        """
        return self.product.get_absolute_url()


    def image_url(self):
        """
        Return the image URL of the associated Product
        """
        return self.product.image.url