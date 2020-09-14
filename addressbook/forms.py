from django import forms
from addressbook.models import Address


class AddressForm(forms.ModelForm):
    
    class Meta:
        model = Address
        fields = Address.FORM_FIELDS