from django import forms
from django.contrib.auth.models import Group, Permission
from accounts.models import Account
from catalog.models import (
    Category, Policy, PolicyGroup, PolicyMembership
)



class PolicyForm(forms.ModelForm):
    
    class Meta:
        model = Policy
        fields = ("daily_limit","weekly_limit", "monthly_limit", "commission",)

class PolicyGroupForm(forms.ModelForm):

    class Meta:
        model = PolicyGroup
        fields = ('name', 'policy',)

class PolicyGroupUpdateForm(forms.ModelForm):
    
    class Meta:
        model = PolicyGroup
        fields = ('name', 'policy', 'members',)

class PolicyGroupUpdateMembersForm(forms.ModelForm):
    
    class Meta:
        model = PolicyGroup
        fields = ('members',)





class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ("user","date_of_birth","country",
                  "city","province","address","zip_code","telefon",
                  "newsletter","is_active_account","balance","account_type",
                  "email_validated", )
        


class TokenForm(forms.Form):
    user = forms.IntegerField()


class GroupFormCreation(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'permissions']


class OrderSoldItemForm(forms.Form):
    product = forms.IntegerField(required=False)
    quantity = forms.IntegerField(required=False)
    status = forms.IntegerField(required=False)
    changed_by = forms.IntegerField()

class OrderItemForm(forms.Form):
    product = forms.IntegerField(required=False)
    quantity = forms.IntegerField(required=False)
    status = forms.IntegerField(required=False)
    changed_by = forms.IntegerField()