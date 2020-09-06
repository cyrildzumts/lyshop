from django.db import models
from django.db.models import Q
from django.shortcuts import reverse
from django.contrib.auth.models import User, Group
from lyshop import conf as GlobalConf
from payment import conf as PaymentConf
import uuid

# Create your models here.

class PaymentPolicy(models.Model):
    """
        Every Business account has a policy set. This policy defines the 
        transfer limit applied to the business account.
        For every transfer going to a business account a commission fee is extracted from 
        the transfer amount. This fee is added the PAY account.

        The monthly_limit is maximal amount allowed to be received by a business account in a month.
        The commission is a percent value that is to be taken from the transfer amount.

    """
    monthly_limit = models.IntegerField(blank=False)
    commission = models.DecimalField(max_digits=GlobalConf.COMMISSION_MAX_DIGITS, decimal_places=GlobalConf.COMMISSION_DECIMAL_PLACES, default=GlobalConf.COMMISSION_DEFAULT)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User, related_name="edited_payment_policies", unique=False, null=True,blank=True, on_delete=models.SET_NULL)
    policy_uuid = models.UUIDField(default=uuid.uuid4, editable=False)



    def __str__(self):
        return "PaymentPolicy {0}".format(self.commission)

    def get_absolute_url(self):
        return reverse("payment:policy-detail", kwargs={"policy_uuid": self.policy_uuid})
    
    def get_dashboard_url(self):
        return reverse("dashboard:policy-detail", kwargs={"policy_uuid": self.policy_uuid})
    
    def get_delete_url(self):
        return reverse("payment:policy-remove", kwargs={"policy_uuid": self.policy_uuid})

    def get_dashboard_delete_url(self):
        return reverse("dashboard:policy-remove", kwargs={"policy_uuid": self.policy_uuid})

    def get_dashboard_update_url(self):
        return reverse("dashboard:policy-update", kwargs={"policy_uuid": self.policy_uuid})
    
    def get_update_url(self):
        return reverse("payment:policy-update", kwargs={"policy_uuid": self.policy_uuid})



class PaymentPolicyGroup(models.Model):
    name = models.CharField(max_length=80)
    policy = models.ForeignKey(PaymentPolicy, on_delete=models.CASCADE, related_name='payment_policy_group')
    policy_id_ref = models.IntegerField(blank=True, null=True)
    #commission = models.DecimalField(max_digits=GlobalConf.COMMISSION_MAX_DIGITS, decimal_places=GlobalConf.COMMISSION_DECIMAL_PLACES, default=GlobalConf.COMMISSION_DEFAULT)
    members = models.ManyToManyField(User, through='PaymentPolicyMembership', through_fields=('group', 'user'), blank=True)
    policy_group_uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("payment:policy-group-detail", kwargs={"group_uuid": self.policy_group_uuid})
    
    def get_dashboard_url(self):
        return reverse("dashboard:policy-group-detail", kwargs={"group_uuid": self.policy_group_uuid})

    def get_update_url(self):
        return reverse("payment:policy-group-update", kwargs={"group_uuid": self.policy_group_uuid})
    
    def get_delete_url(self):
        return reverse("payment:policy-group-remove", kwargs={"group_uuid": self.policy_group_uuid})



class PaymentPolicyMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(PaymentPolicyGroup, on_delete=models.CASCADE)
    membership_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    #modified_by = models.ForeignKey(User, related_name="modified_membership", unique=False, null=True,blank=True, on_delete=models.SET_NULL)
    #added_by = models.ForeignKey(User, related_name="added_membership", unique=False, null=True,blank=True, on_delete=models.SET_NULL)




class Payment(models.Model):
    seller = models.ForeignKey(User, related_name='payments', blank=False, null=True, on_delete=models.SET_NULL)
    amount = models.DecimalField(blank=False, null=False, max_digits=GlobalConf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=GlobalConf.PRODUCT_PRICE_DECIMAL_PLACES)
    balance_amount = models.DecimalField(blank=False, null=False, max_digits=GlobalConf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=GlobalConf.PRODUCT_PRICE_DECIMAL_PLACES)
    pay_username = models.CharField(max_length=64)
    policy = models.ForeignKey(PaymentPolicy, blank=True, null=True, on_delete=models.SET_NULL)
    monthly_limit = models.IntegerField(blank=False)
    payment_mode = models.IntegerField(blank=False, null=False, choices=PaymentConf.PAYMENT_MODE)
    payment_schedule = models.IntegerField(default=PaymentConf.PAYMENT_DATE_LAST_FRIDAY ,blank=False, null=False, choices=PaymentConf.PAYMENT_DATE)
    commission = models.DecimalField(max_digits=GlobalConf.COMMISSION_MAX_DIGITS, decimal_places=GlobalConf.COMMISSION_DECIMAL_PLACES, default=GlobalConf.COMMISSION_DEFAULT)
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    payment_date = models.DateTimeField(blank=True, null=True)
    payment_uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return f"Payment {seller.username} - {amount}"

    def get_absolute_url(self):
        return reverse("payment:payment-detail", kwargs={"payment_uuid": self.payment_uuid})
    
    def get_dashboard_url(self):
        return reverse("dashboard:payment-detail", kwargs={"payment_uuid": self.payment_uuid})



class PaymentDate(models.Model):
    name = models.CharField(default=PaymentConf.PAYMENT_DATE_LAST_FRIDAY, max_length=64, blank=False, null=False)
    payment_schedule = models.IntegerField(default=PaymentConf.PAYMENT_DATE_LAST_FRIDAY, blank=False, null=False, choices=PaymentConf.PAYMENT_DATE)
    date_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    
    def __str__(self):
        return f"PaymentDate {self.name}"

    def get_absolute_url(self):
        return reverse("payment:payment-date-detail", kwargs={"date_uuid": self.date_uuid})
    
    def get_dashboard_url(self):
        return reverse("dashboard:payment-date-detail", kwargs={"date_uuid": self.date_uuid})



class PaymentDateGroup(models.Model):
    name = models.CharField(max_length=80)
    schedule = models.ForeignKey(PaymentDate, on_delete=models.CASCADE, related_name='payment_date_group')
    members = models.ManyToManyField(User, through='PaymentDateGroupMembership', through_fields=('group', 'user'), blank=True, null=True)
    group_uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return f"PaymentDateGroup {self.name}"

    def get_absolute_url(self):
        return reverse("payment:payment-date-group-detail", kwargs={"group_uuid": self.policy_group_uuid})
    
    def get_dashboard_url(self):
        return reverse("dashboard:payment-date-group-detail", kwargs={"group_uuid": self.policy_group_uuid})

    def get_update_url(self):
        return reverse("payment:payment-date-group-update", kwargs={"group_uuid": self.policy_group_uuid})
    
    def get_delete_url(self):
        return reverse("payment:payment-date-group-remove", kwargs={"group_uuid": self.policy_group_uuid})


class PaymentDateGroupMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(PaymentDateGroup, on_delete=models.CASCADE)
    membership_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


class PaymentHistory(models.Model):
    payment_ref_id = models.IntegerField(blank=False, null=False)
    amount = models.DecimalField(blank=False, null=False, max_digits=GlobalConf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=GlobalConf.PRODUCT_PRICE_DECIMAL_PLACES)
    payment = models.ForeignKey(Payment, related_name="payment_history", blank=True, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    history_uuid = models.UUIDField(default=uuid.uuid4, editable=False)    


    def __str__(self):
        return f"PaymentHistory {self.id}"