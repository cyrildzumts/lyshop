from django.db import models
from django.contrib.auth.models import User
from dashboard import Constants


# Create your models here.

class AccessPermissions(models.Model):
   


    class Meta:
        managed = False
        permissions = [
            (Constants.DASHBOARD_VIEW_PERM, 'Dashboard Can view Dashboard'),
            (Constants.GROUP_ADD_PERM, 'Dashboard Can create a Group'),
            (Constants.GROUP_CHANGE_PERM, 'Dashboard Can change a Group'),
            (Constants.GROUP_DELETE_PERM, 'Dashboard Can delete a Group'),
            (Constants.GROUP_VIEW_PERM, 'Dashboard Can view Group'),

            (Constants.TOKEN_GENERATE_PERM, 'Dashboard Can generate Token'),



            (Constants.BRAND_VIEW_PERM, 'Dashboard Can View Brand'),
            (Constants.BRAND_CHANGE_PERM, 'Dashboard Can Change Brand'),
            (Constants.BRAND_ADD_PERM, 'Dashboard Can Add Brand'),
            (Constants.BRAND_DELETE_PERM, 'Dashboard Can Delete Brand'),


            (Constants.CATEGORY_VIEW_PERM, 'Dashboard Can View Category'),
            (Constants.CATEGORY_CHANGE_PERM, 'Dashboard Can Change Category'),
            (Constants.CATEGORY_ADD_PERM, 'Dashboard Can Add Category'),
            (Constants.CATEGORY_DELETE_PERM, 'Dashboard Can Delete Category'),

            (Constants.POLICY_VIEW_PERM, 'Dashboard Can View Policy'),
            (Constants.POLICY_CHANGE_PERM, 'Dashboard Can Change Policy'),
            (Constants.POLICY_ADD_PERM, 'Dashboard Can Add Policy'),
            (Constants.POLICY_DELETE_PERM, 'Dashboard Can Delete Policy'),

            (Constants.POLICY_GROUP_VIEW_PERM, 'Dashboard Can View Policy Group'),
            (Constants.POLICY_GROUP_CHANGE_PERM, 'Dashboard Can Change Policy Group'),
            (Constants.POLICY_GROUP_ADD_PERM, 'Dashboard Can Add Policy Group'),
            (Constants.POLICY_GROUP_DELETE_PERM, 'Dashboard Can Delete Policy Group'),

            (Constants.POLICY_MEMBERSHIP_VIEW_PERM, 'Dashboard Can View Policy Membership'),
            (Constants.POLICY_MEMBERSHIP_CHANGE_PERM, 'Dashboard Can Change Policy Membership'),
            (Constants.POLICY_MEMBERSHIP_ADD_PERM, 'Dashboard Can Add Policy Membership'),
            (Constants.POLICY_MEMBERSHIP_DELETE_PERM, 'Dashboard Can Delete Policy Membership'),

            (Constants.PRODUCT_VIEW_PERM, 'Dashboard Can View Product'),
            (Constants.PRODUCT_CHANGE_PERM, 'Dashboard Can Change Product'),
            (Constants.PRODUCT_ADD_PERM, 'Dashboard Can Add Product'),
            (Constants.PRODUCT_DELETE_PERM, 'Dashboard Can Delete Product'),

            (Constants.USER_VIEW_PERM, 'Dashboard Can View User'),
            (Constants.USER_CHANGE_PERM, 'Dashboard Can Change User'),
            (Constants.USER_ADD_PERM, 'Dashboard Can Add User'),
            (Constants.USER_DELETE_PERM, 'Dashboard Can Delete User'),

            (Constants.ORDER_VIEW_PERM, 'Dashboard Can View Order'),
            (Constants.ORDER_CHANGE_PERM, 'Dashboard Can Change Order'),
            (Constants.ORDER_ADD_PERM, 'Dashboard Can Add Order'),
            (Constants.ORDER_DELETE_PERM, 'Dashboard Can Delete Order'),

            (Constants.PAYMENT_VIEW_PERM, 'Dashboard Can View Payment'),
            (Constants.PAYMENT_CHANGE_PERM, 'Dashboard Can Change Payment'),
            (Constants.PAYMENT_ADD_PERM, 'Dashboard Can Add Payment'),
            (Constants.PAYMENT_DELETE_PERM, 'Dashboard Can Delete Payment'),

            (Constants.COUPON_VIEW_PERM, 'Dashboard Can View Coupon'),
            (Constants.COUPON_CHANGE_PERM, 'Dashboard Can Change Coupon'),
            (Constants.COUPON_ADD_PERM, 'Dashboard Can Add Coupon'),
            (Constants.COUPON_DELETE_PERM, 'Dashboard Can Delete Coupon'),

            (Constants.SHIPMENT_VIEW_PERM, 'Dashboard Can View Shipment'),
            (Constants.SHIPMENT_CHANGE_PERM, 'Dashboard Can Change Shipment'),
            (Constants.SHIPMENT_ADD_PERM, 'Dashboard Can Add Shipment'),
            (Constants.SHIPMENT_DELETE_PERM, 'Dashboard Can Delete Shipment')
        ]


class LoginReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, unique=False, related_name="login_report", blank=True, null=True)
    is_anonymous_user = models.BooleanField(default=True)
    user_agent = models.CharField(max_length=256, blank=True, null=True)
    date_login = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()

    def __str__(self):
        return f"LoginReport {self.user} - Date {self.date_login} - IP {self.ip_address}"
    
    @staticmethod
    def report(user):
        if not isinstance(user, User):
            raise ValueError(f"{user} is not an user instance")
        queryset = LoginReport.objects.filter(user=user)


class UserAction(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, unique=False, related_name="actions", blank=True, null=True)
    is_anonymous_user = models.BooleanField(default=True)
    user_agent = models.CharField(max_length=256, blank=True, null=True)
    request_method = models.CharField(max_length=128, blank=True, null=True)
    query_string = models.CharField(max_length=256, blank=True, null=True)
    remote_host = models.CharField(max_length=128, blank=True, null=True)
    requested_path = models.CharField(max_length=256, blank=True, null=True)
    date_action = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()

    def __str__(self):
        return f"UserAction {self.user} - Date {self.date_action} - IP {self.ip_address}"
    
    @staticmethod
    def report(user):
        if not isinstance(user, User):
            raise ValueError(f"{user} is not an user instance")
        queryset = UserAction.objects.filter(user=user)
    
    @staticmethod
    def user_action(sender, request, user, **kwargs):
        UserAction.objects.create(user=user, user_agent=request.META.HTTP_USER_AGENT, is_anonymous_user=user.is_anonymous,
            ip_address=request.META.REMOTE_ADDR, request_method=request.META.REQUEST_METHOD, query_string=request.META.QUERY_STRING,
            remote_host=request.META.REMOTE_HOST, requested_path=request.get_full_path())


class LoggedUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL,related_name="logged_user", blank=True, null=True)
    user_agent = models.CharField(max_length=256, blank=True, null=True)
    request_method = models.CharField(max_length=128, blank=True, null=True)
    date_login = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()

    def __str__(self):
        return f"LoggedUser {self.user} - Date {self.date_login} - IP {self.ip_address}"
    
    @staticmethod
    def report(user):
        if not isinstance(user, User):
            raise ValueError(f"{user} is not an user instance")
        queryset = LoggedUser.objects.filter(user=user)

    @staticmethod
    def user_logged_in(sender, requet, user, **kwargs):
        LoggedUser.objects.create(user=user, user_agent=request.META.HTTP_USER_AGENT, 
            ip_address=request.META.REMOTE_ADDR, request_method=request.META.REQUEST_METHOD)
    

    