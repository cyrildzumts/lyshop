from django.shortcuts import render
from django.db.models import F, Q, Sum, Count
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist
from catalog.models import Product, ProductVariant
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
    
    sold_product_list = SoldProduct.objects.filter(seller=request.user).select_related()[:5]
    recent_products = Product.objects.filter(sold_by=request.user)[:5]
    seller_product_queryset = ProductVariant.objects.filter(is_active=True, product__sold_by=request.user)
    product_count = seller_product_queryset.aggregate(product_count=Sum('quantity')).get('product_count', 0)
    number_sold_products = SoldProduct.objects.filter(seller=request.user).count()
    context = {
        'page_title' : page_title,
        'balance' : balance,
        'number_sold_products' : number_sold_products,
        'recent_sold_products': sold_product_list,
        'recent_products' : recent_products,
        'product_count': product_count
    }
    return render(request, template_name, context)


@login_required
def product_list(request):
    username = request.user.username
    '''
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_view_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    '''

    template_name = 'dashboard/product_list.html'
    page_title = _('Products')
    context = {
        'page_title': page_title,
    }

    queryset = Product.objects.filter(is_active=True, sold_by=request.user).order_by('-created_at')
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, 10)
    try:
        list_set = paginator.page(page)
    except PageNotAnInteger:
        list_set = paginator.page(1)
    except EmptyPage:
        list_set = None
    context['page_title'] = page_title
    context['product_list'] = list_set
    #context.update(get_view_permissions(request.user))
    return render(request,template_name, context)



@login_required
def product_variant_list(request, product_uuid):
    username = request.user.username
    '''
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_view_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    '''

    template_name = 'dashboard/product_list.html'
    page_title = _('Products')
    context = {
        'page_title': page_title,
    }

    queryset = ProductVariant.objects.filter(is_active=True, product__sold_by=request.user ,product__product_uuid=product_uuid).order_by('-created_at')
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, 10)
    try:
        list_set = paginator.page(page)
    except PageNotAnInteger:
        list_set = paginator.page(1)
    except EmptyPage:
        list_set = None
    context['page_title'] = page_title
    context['product_list'] = list_set
    #context.update(get_view_permissions(request.user))
    return render(request,template_name, context)


@login_required
def product_detail(request, product_uuid):
    pass



@login_required
def product_variant_detail(request, product_uuid):
    pass


@login_required
def sold_product_list(request):
    pass





@login_required
def sold_product_detail(request, product_uuid):
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

