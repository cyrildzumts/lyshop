
from django import forms
from payment.models import PaymentPolicy, PaymentPolicyGroup, PaymentPolicyMembership


class PaymentPolicyForm(forms.ModelForm):
    
    class Meta:
        model = PaymentPolicy
        fields = ("monthly_limit", "commission",)

class PaymentPolicyGroupForm(forms.ModelForm):

    class Meta:
        model = PaymentPolicyGroup
        fields = ('name', 'policy', 'members')

class PaymentPolicyGroupUpdateForm(forms.ModelForm):
    
    class Meta:
        model = PaymentPolicyGroup
        fields = ('name', 'policy', 'members',)

class PaymentPolicyGroupUpdateMembersForm(forms.ModelForm):
    
    class Meta:
        model = PaymentPolicyGroup
        fields = ('members',)