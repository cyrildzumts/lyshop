from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.http import Http404
from django.utils.translation import gettext_lazy as _
from orders import orders_service
from shipment import shipment_service
from orders import commons
from vendors.models import SoldProduct
from orders.forms import ShippingAddressForm, BillingAddressForm, PaymentRequestForm, PaymentOptionForm
from orders.models import Order, OrderItem, Address, PaymentRequest, OrderStatusHistory
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
    queryset = Order.objects.filter(user=request.user).order_by('-created_at')
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

    order = get_object_or_404(Order,user=request.user, order_uuid=order_uuid)
    orderItems = OrderItem.objects.filter(order=order)
    shipment = shipment_service.find_order_shipment(order)
    context = {
        'page_title': page_title,
        'order': order,
        'shipment' : shipment,
        'orderItems': orderItems,
        'order_is_cancelable' :  orders_service.is_cancelable(order)
    }
    return render(request,template_name, context)


@login_required
def cancel_order(request, order_uuid):
    order = get_object_or_404(Order, order_uuid=order_uuid, user=request.user)
    canceled = orders_service.cancel_order(order)
    if canceled:
        messages.success(request, "Order canceled")
    else:
        messages.error(request, "Order could not be canceled")

    return redirect(order)


@login_required
def order_cancel(request, order_uuid):
    order = get_object_or_404(Order,user=request.user, order_uuid=order_uuid)
        
    if orders_service.is_cancelable(order):
        #Order.objects.filter(id=order.id).update(status=commons.ORDER_CANCELED, last_changed_by=request.user)
        orders_service.cancel_order(order)
        OrderStatusHistory.objects.create(order_status=commons.ORDER_CANCELED, order=order, order_ref_id=order.id, changed_by=request.user)
        messages.success(request, "Your order has been canceled")
        logger.info(f"Order {order.id} canceled by user {request.user.username}")
    else:
        messages.error(request, "Error. Your order can no more be canceled")
    
    return redirect(order)



@login_required
def checkout(request):
    cart = orders_service.get_user_cart(request.user)
    template_name = 'orders/checkout.html'
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
                order = orders_service.create_order_from_cart(user=request.user)
                logger.debug("Order ready. Now preparing payment data")

                try:
                    payment_data = {
                        'requester_name': settings.PAY_USERNAME,
                        'amount': order.total,
                        'customer_name': request.user.get_full_name(),
                        'quantity': cart.quantity,
                        'description': settings.PAY_REQUEST_DESCRIPTION,
                        'country' : shipping_address_form.cleaned_data.get('shipping_country'),
                        'redirect_success_url': request.build_absolute_uri(reverse('orders:checkout-success', kwargs={'order_uuid': order.order_uuid})),
                        'redirect_failed_url': request.build_absolute_uri(reverse('orders:checkout-failed', kwargs={'order_uuid': order.order_uuid})),
                        'product_name' : 'LYSHOP'
                    }
                    logger.debug("Sending request payment")
                except Exception as e:
                    logger.error("Eror on prepayring payment data")
                    logger.exception(e)
                    raise e
                
                #cart_items_queryset = orders_service.get_user_cartitems(request.user)
                response = orders_service.request_payment(payment_data)
                if response:
                    response_json = response.json()
                    logger.debug("request payment succeed")
                    
                    orders_service.order_clear_cart(request.user)
                    logger.debug("Creating Payment Request")
                    payment_data['token'] = response_json['token']
                    payment_data['pay_url'] = response_json['url']
                    payment_data['order'] = order
                    payment_data['customer'] = request.user
                    payment_data['verification_code'] = response_json['verification_code']
                    try:
                        payment_request = PaymentRequest.objects.create(**payment_data)
                        messages.success(request,"order has been successfully submitted")
                        return redirect('orders:checkout-redirect-payment', request_uuid=payment_request.request_uuid)
                    except Exception as e:
                        messages.error(request,"An error occured during processing Order")
                        logger.error(f"Error on creating PaymentRequest object")
                        logger.exception(e)
                    
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


def checkout_redirect_payment(request, request_uuid):
    page_title = _("Checkout Redirect to PAY") + " - " + settings.SITE_NAME
    template_name = "orders/checkout_redirect_payment.html"
    payment_request = None
    #queryset = PaymentRequest.objects.filter(request_uuid=request_uuid, order__order_uuid=order_uuid)
    try:
        payment_request = PaymentRequest.objects.get(request_uuid=request_uuid)
    except PaymentRequest.DoesNotExists:
        logger.error(f"checkout_redirect view call with invalid  requestuuid \"{request_uuid}\". No Paymentrequest found")
        raise Http404
    context = {
        'page_title' : page_title,
        'payment_request': payment_request
    }
    return render(request, template_name, context)

def checkout_success(request, order_uuid):
    page_title = _("Checkout succeed") + " - " + settings.SITE_NAME
    template_name = "orders/checkout_success.html"
    order = None
    payment_request = None
    queryset = PaymentRequest.objects.filter(order__order_uuid=order_uuid, customer=request.user)
    if not queryset.exists():
        logger.error(f"checkout_success view call with invalid order uuid \"{order_uuid}\". No order found")
        raise Http404
    queryset.update(status=commons.ORDER_PAID, payment_status=commons.PAYMENT_PAID, is_paid=True)
    payment_request = queryset.first()
    order = payment_request.order
    Order.objects.filter(order_uuid=order_uuid).update(status=commons.ORDER_PAID)
    OrderStatusHistory.objects.create(order=order, order_status=commons.ORDER_PAID, order_ref_id=order.id, changed_by=request.user)
    flag = orders_service.mark_product_sold(order)
    context = {
        'page_title' : page_title,
        'order' : order,
        'payment_request': payment_request
    }
    return render(request, template_name, context)


def checkout_failed(request, order_uuid):
    page_title = _("Checkout failed") + " - " + settings.SITE_NAME
    template_name = "orders/checkout_failed.html"
    order = None
    payment_request = None
    #queryset = PaymentRequest.objects.filter(request_uuid=request_uuid, order__order_uuid=order_uuid)
    try:
        payment_request = PaymentRequest.objects.filter(order__order_uuid=order_uuid, customer=request.user).get()
        logger.info(f"Checkout failed : found payment request with order uuid \"{order_uuid}\"")
        order = payment_request.order
        PaymentRequest.objects.filter(id=payment_request.id).update(payment_status=commons.PAYMENT_FAILED)
        Order.objects.filter(order_uuid=order_uuid).update(status=commons.ORDER_PAYMENT_FAILED)
        OrderStatusHistory.objects.create(order=order, order_status=commons.ORDER_PAYMENT_FAILED, order_ref_id=order.id, changed_by=request.user)
        orders_service.cancel_order(order)
        #order = payment_request.order
    except PaymentRequest.DoesNotExist:
        logger.error(f"checkout_failed view call with invalid order uuid \"{order_uuid}\". No order found")
        raise Http404

    context = {
        'page_title' : page_title,
        #'order' : order,
        'payment_request': payment_request
    }
    return render(request, template_name, context)


