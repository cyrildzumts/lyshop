from django.shortcuts import render, redirect
from django.utils.translation import gettext_lazy as _
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from orders import orders_service
from orders import commons
from orders.forms import ShippingAddressForm, BillingAddressForm, PaymentRequestForm, PaymentOptionForm
from orders.models import Order, OrderItem, Address, PaymentRequest
from lyshop import settings, utils
from http import HTTPStatus
import json
import logging
import uuid


logger = logging.getLogger(__name__)

# Create your views here.

@login_required
def orders(request):

    username = request.user.username
    context = {}
    queryset = Order.objects.filter(user=request.user)
    template_name = "orders/order_list.html"
    page_title = _("Dashboard Orders") + " - " + settings.SITE_NAME
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, utils.PAGINATED_BY)
    try:
        list_set = paginator.page(page)
    except PageNotAnInteger:
        list_set = paginator.page(1)
    except EmptyPage:
        list_set = None
    context['page_title'] = page_title
    context['orders'] = list_set
    return render(request,template_name, context)

@login_required
def order_detail(request, order_uuid=None):
    template_name = 'orders/order_detail.html'
    username = request.user.username
    page_title = _('Order Detail')
    order = get_object_or_404(Order, order_uuid=order_uuid)
    orderItems = OrderItem.objects.filter(order=order)
    context = {
        'page_title': page_title,
        'order': order,
        'orderItems': orderItems,
    }
    return render(request,template_name, context)

@login_required
def checkout(request):
    cart = orders_service.get_user_cart(request.user)
    template_name = 'orders/order.html'
    context = {
        'page_title' : _("Checkout") + ' - ' + settings.SITE_NAME
    }
    if not cart or (cart.quantity == 0 or cart.amount == 0.0):
        messages.error(request, _("Your Cart is empty"))
        return redirect('catalog:catalog-home')
    if request.method == 'POST':
        postdata = utils.get_postdata(request)
        shipping_address_form = ShippingAddressForm(postdata)
        shipping_address_form_is_valid = shipping_address_form.is_valid()
        payment_option_form = PaymentOptionForm(postdata)
        payment_option_form_is_valid = payment_option_form.is_valid()
        use_shipping_addr_as_billing_addr = False
        if shipping_address_form_is_valid and payment_option_form_is_valid:
            logger.debug("Order Form is valid")
            use_shipping_addr_as_billing_addr = shipping_address_form.cleaned_data.get('billing_shipping')
            payment_option = payment_option_form.cleaned_data.get('payment_option')
            logger.debug(f"Selected Payment Option : {payment_option}")
            if payment_option == commons.PAYMENT_PAY_WITH_PAY:
                payment_data = {
                    'requester_name': settings.PAY_USERNAME,
                    'amount': cart.amount,

                    'customer_name': request.user.get_full_name(),
                    'quantity': cart.quantity,
                    'description': settings.PAY_REQUEST_DESCRIPTION,
                    'country' : shipping_address_form.cleaned_data.get('shipping_country'),
                    'product_name' : 'LYSHOP'
                }
                logger.debug("Sending request payment")
                order = orders_service.create_order_from_cart(user=request.user)
                #cart_items_queryset = orders_service.get_user_cartitems(request.user)
                response = orders_service.request_payment(payment_data)
                if response:
                    logger.debug("request payment succeed")
                    orders_service.order_clear_cart(request.user)
                    PaymentRequest.objects.create(**payment_data, token=response['token'])
                else:
                    logger.debug("request payment failed")
                
            if not use_shipping_addr_as_billing_addr:
                logger.debug("User is using a different address for billing")
                billing_addr_form = BillingAddressForm(postdata)
                if billing_addr_form.is_valid():
                    logger.debug("User submitted billing address")

        else:
            if not shipping_address_form_is_valid:
                logger.error("Order Form is not valid. Error on ShipingAddressForm")
                logger.error(shipping_address_form.errors)
            if not payment_option_form_is_valid:
                logger.error("Order Form is not valid. Error on PaymentOptionForm")
                logger.error(payment_option_form.errors)
        logger.debug("Processing Checkout POST request")
    
    elif request.method == 'GET':
        logger.debug("Processing Checkout POST request")
    return render(request, template_name, context)