from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import login_required
from catalog.models import Product, ProductVariant
from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist
from accounts.models import Account
from lyshop import settings
from vendors.models import Balance, BalanceHistory, VendorPayment, VendorPaymentHistory, SoldProduct
import logging

logger = logging.getLogger(__name__)

# Create your views here.
@login_required
def vendor_home(request):
    template_name = "vendors/vendor_home.html"
    page_title = _("Vendor-Home")

    balance = None
    try:
        balance = Balance.objects.get(user=request.user)
    except ObjectDoesNotExist as e:
        logger.warn("Request User has no balance")
    
    sold_product_list = SoldProduct.objects.filter(seller=request.user)[:5]
    number_sold_products = SoldProduct.objects.filter(seller=request.user).count()
    context = {
        'page_title' : page_title,
        'balance' : balance,
        'number_sold_products' : number_sold_products,
        'recent_sold_products': sold_product_list
    }
    return render(request, template_name, context)


@login_required
def product_list(request):
    pass



@login_required
def product_detail(request, product_uuid):
    pass

@login_required
def balance_history(request, balance_uuid):
    pass


@login_required
def balance_history_detail(request, history_uuid):
    pass

@login_required
def vendor_payments(request):
    pass


@login_required
def payment_details(request, payment_uuid):
    pass


@login_required
def payment_history(request):
    pass


@login_required
def request_payment(request):
    pass

