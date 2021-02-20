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
        if Wishlist.objects.filter(name=name, customer=customer).exists():
            raise ValidationError("Name already in use.")


class AddToWishlistForm(forms.Form):
    product_uuid = forms.UUIDField()
    wishlist_uuid = forms.UUIDField()


class CreateAndAddWishlistForm(forms.Form):
    product_uuid = forms.UUIDField()
    name = forms.CharField(max_length=64)
    customer = forms.IntegerField()

    def clean(self):
        super().clean()
        name = self.cleaned_data.get('name')
        customer = self.cleaned_data.get('customer')
        if Wishlist.objects.filter(name=name, customer__id=customer).exists():
            raise ValidationError("Name already in use.")




class RenameWishlistForm(forms.Form):
    name = forms.CharField(max_length=64)
    wishlist_uuid = forms.UUIDField()
    customer = forms.IntegerField()

    def clean(self):
        super().clean()
        name = self.cleaned_data.get('name')
        customer = self.cleaned_data.get('customer')
        if Wishlist.objects.filter(name=name, customer__id=customer).exists():
            raise ValidationError("Name already in use.")
