
from django import forms
from payment.models import PaymentPolicy, PaymentPolicyGroup, PaymentPolicyMembership, PaymentDate, PaymentDateGroup


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


class PaymentDateForm(forms.ModelForm):
    
    class Meta:
        model = PaymentDate
        fields = ("name", "payment_schedule",)

class PaymentDateGroupForm(forms.ModelForm):

    class Meta:
        model = PaymentDateGroup
        fields = ('name', 'schedule', 'members')
        

class PaymentDateGroupUpdateForm(forms.ModelForm):
    
    class Meta:
        model = PaymentDateGroup
        fields = ('name', 'schedule', 'members',)

class PaymentDateGroupUpdateMembersForm(forms.ModelForm):
    
    class Meta:
        model = PaymentDateGroup
        fields = ('members',)