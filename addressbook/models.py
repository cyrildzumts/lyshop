from django.db import models
from django.contrib.auth.models import User
from addressbook import constants as Addressbook_Constants
from django.shortcuts import reverse
import uuid

# Create your models here.
class Address(models.Model):
    user = models.ForeignKey(User, related_name='addresses', blank=True, null=True, on_delete=models.CASCADE)
    city = models.CharField(max_length=32)
    firstname= models.CharField(max_length=32, blank=True, null=True)
    lastname = models.CharField(max_length=64, blank=True, null=True)
    country = models.CharField(max_length=32)
    phone_number = models.CharField(max_length=32, blank=True, null=True)
    postal_code = models.IntegerField(blank=True, null=True)
    address_type = models.IntegerField(default=Addressbook_Constants.ADDRESS_FOR_BILLING_AND_SHIPPING, blank=True, null=True, choices=Addressbook_Constants.ADDRESS_TYPES)
    address_extra = models.CharField(max_length=64, blank=True, null=True)
    street = models.CharField(max_length=64, blank=True, null=True)
    house_number = models.IntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True, blank=True, null=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    last_edited_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    last_changed_by = models.ForeignKey(User, related_name='edited_addresses', blank=True, null=True, on_delete=models.SET_NULL)
    address_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    FORM_FIELDS = ['user', 'city', 'firstname', 'lastname', 'country', 'postal_code','phone_number', 'address_extra', 'street','house_number', 'is_active', 'last_changed_by',]

    def __str__(self):
        return f"Addressbook {self.user.username} {self.pk}"
    
    def get_absolute_url(self):
        return reverse("addressbook:address", kwargs={"address_uuid": self.address_uuid})
    
    def get_update_url(self):
        return reverse("addressbook:address-update", kwargs={"address_uuid": self.address_uuid})
    
    def get_delete_url(self):
        return reverse("addressbook:address-delete", kwargs={"address_uuid": self.address_uuid})
    
    

    