from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from wishlist.models import Wishlist, WishlistItem
import logging

logger = logging.getLogger(__name__)


class WishlistForm(forms.ModelForm):
    
    class Meta:
        model = Wishlist
        fields = Wishlist.FORM_FIELDS
    

    def clean(self):
        super().clean()
        name = self.cleaned_data.get('name')
        customer = self.cleaned_data.get('customer')
        logger.debug(f"Wishlist clean  : name \"{name}\" : customer : \"{customer}\" - typeof customer {type(customer)} -  typeof name {type(name)}")
        if Wishlist.objects.filter(name=name, customer=customer).exists():
            raise ValidationError("Name already in use.")



