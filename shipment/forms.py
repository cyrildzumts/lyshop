from shipment.models import Shipment


class ShipmentForm(forms.ModelForm):
    
    class Meta:
        model = Shipment
        fields = Shipment.DEFAULT_UPDATE_FIELDS
