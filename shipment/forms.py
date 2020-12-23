from django import forms
from shipment.models import Shipment, ShipMode


class ShipmentForm(forms.ModelForm):
    
    class Meta:
        model = Shipment
        fields = Shipment.DEFAULT_UPDATE_FIELDS


class ShipModeForm(forms.ModelForm):

    class Meta:
        model = ShipMode
        fields = []
