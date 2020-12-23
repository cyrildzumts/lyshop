from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.http import Http404
from django.utils.translation import gettext_lazy as _
from orders import orders_service
from addressbook.forms import AddressModelForm, AddressForm
from addressbook import addressbook_service
from addressbook import constants as Addressbook_Constants
from shipment import shipment_service, constants as SHIPMENT_CONSTANTS
from core.filters import filters
from orders import commons
from vendors.models import SoldProduct
from orders.forms import ShippingAddressForm, BillingAddressForm, PaymentRequestForm, PaymentOptionForm, OrderFilterOption
from orders.models import Order, OrderItem, PaymentRequest, OrderStatusHistory
from lyshop import settings, utils, conf as GLOBAL_CONF
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
    
    template_name = "orders/order_list.html"
    page_title = _("My Orders") + " - " + settings.SITE_NAME
    queryDict = request.GET.copy()
    field_filter = filters.Filter(Order, queryDict)
    queryset = field_filter.apply_filter()
    selected_filters = field_filter.selected_filters

    if queryset is None:
        queryset = Order.objects.filter(user=request.user).order_by('-created_at')
    else:
        queryset = queryset.filter(user=request.user).order_by('-created_at')
    
    logger.debug(f"selected_filters : {field_filter.selected_filters}")
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, GLOBAL_CONF.PAGINATED_BY)
    try:
        list_set = paginator.page(page)
    except PageNotAnInteger:
        list_set = paginator.page(1)
    except EmptyPage:
        list_set = None
    context['page_title'] = page_title
    context['orders'] = list_set
    context['ORDER_STATUS'] = commons.ORDER_STATUS
    context['PAYMENT_OPTIONS'] = commons.PAYMENT_OPTIONS
    context['SELECTED_FILTERS'] = selected_filters
    context['FILTER_CONFIG'] = Order.FILTER_CONFIG
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
    canceled = orders_service.cancel_order(order, request.user)
    if canceled:
        messages.success(request, "Order canceled")
    else:
        messages.error(request, "Order could not be canceled")

    return redirect(order)


@login_required
def order_cancel(request, order_uuid):
    order = get_object_or_404(Order,user=request.user, order_uuid=order_uuid)
        
    if orders_service.is_cancelable(order):
        orders_service.cancel_order(order, request.user)
        OrderStatusHistory.objects.create(order_status=commons.ORDER_CANCELED, order=order, order_ref_id=order.id, changed_by=request.user)
        messages.success(request, "Your order has been canceled")
        logger.info(f"Order {order.id} canceled by user {request.user.username}")
    else:
        messages.error(request, "Error. Your order can no more be canceled")
    
    return redirect(order)



@login_required
def checkout(request):
    #TODO Refactore this views : move business logic to order_service
    cart = orders_service.get_user_cart(request.user)
    template_name = 'orders/checkout.html'
    address_list = addressbook_service.get_addresses(request.user)
    address = None
    if address_list.filter(is_favorite=True).exists():
        address = address_list.filter(is_favorite=True).first()
    context = {
        'page_title' : _("Checkout") + ' - ' + settings.SITE_NAME,
        'address_list': address_list,
        'address': address,
        'ADDRESS_TYPES' : Addressbook_Constants.ADDRESS_TYPES,
        'cart' : cart,
        'cartitems' : orders_service.get_user_cartitems(request.user),
        'payment_methods' : orders_service.get_payment_methods(filter_active=True),
        'PAYMENT_OPTIONS': commons.ORDER_PAYMENT_OPTIONS,
        'SHIP_MODE' : SHIPMENT_CONSTANTS.SHIP_MODE,
        'ship_modes' : shipment_service.get_ship_modes()
    }
    if not cart or (cart.quantity == 0 or cart.amount == 0.0):
        messages.error(request, _("Your Cart is empty"))
        return redirect('catalog:catalog-home')
    if request.method == 'POST':
        result = orders_service.process_order(request.user, request)
        if result.get('success'):
            if result.get('order').payment_option == commons.PAY_AT_ORDER:
                return redirect(result.get(commons.KEY_REDIRECT_PAYMENT_URL))
            else:
                return redirect(result.get(commons.KEY_REDIRECT_SUCCESS_URL))
        else:
            messages.error(request, message=result.get('msg'))
            logger.warn("Order Checkout failed")
            if result.get(commons.KEY_REDIRECT_FAILED_URL):
                return redirect(result.get(commons.KEY_REDIRECT_FAILED_URL))
    
    return render(request, template_name, context)



@login_required
def checkout_old(request):
    #TODO Refactore this viewsmove business logic to order_service
    cart = orders_service.get_user_cart(request.user)
    template_name = 'orders/checkout.html'
    address_list = addressbook_service.get_addresses(request.user)
    address = None
    if address_list.exists():
        address = address_list.first()
    context = {
        'page_title' : _("Checkout") + ' - ' + settings.SITE_NAME,
        'address_list': address_list,
        'address': address,
        'ADDRESS_TYPES' : Addressbook_Constants.ADDRESS_TYPES,
        'cart' : cart,
        'cartitems' : orders_service.get_user_cartitems(request.user),
        'payment_methods' : orders_service.get_payment_methods(filter_active=True),
        'PAYMENT_OPTIONS': commons.ORDER_PAYMENT_OPTIONS,
    }
    country = ''
    if not cart or (cart.quantity == 0 or cart.amount == 0.0):
        messages.error(request, _("Your Cart is empty"))
        return redirect('catalog:catalog-home')
    if request.method == 'POST':
        postdata = utils.get_postdata(request)
        #result = orders_service.process_order(request.user, postdata)
        if not address:
            addressForm = AddressForm(postdata)
            if addressForm.is_valid():
                logger.info("AddressForm is Valid")
                address = addressForm.save()
                country = address.country
            else:
                logger.info("AddressForm is not Valid")

        payment_option_form = PaymentOptionForm(postdata)
        payment_option_form_is_valid = payment_option_form.is_valid()
        if  payment_option_form_is_valid:
            logger.debug("Order Form is valid")
            
            payment_option = payment_option_form.cleaned_data.get('payment_option')
            logger.debug(f"Selected Payment Option : {payment_option}")
            if payment_option == commons.PAY_WITH_PAY:
                order = orders_service.create_order_from_cart(user=request.user, address=address)
                logger.debug("Order ready. Now preparing payment data")

                try:
                    payment_data = {
                        'requester_name': settings.PAY_USERNAME,
                        'amount': order.total,
                        'customer_name': request.user.get_full_name(),
                        'quantity': cart.quantity,
                        'description': settings.PAY_REQUEST_DESCRIPTION,
                        'country' : country,
                        'redirect_success_url': request.build_absolute_uri(reverse('orders:checkout-success', kwargs={'order_uuid': order.order_uuid})),
                        'redirect_failed_url': request.build_absolute_uri(reverse('orders:checkout-failed', kwargs={'order_uuid': order.order_uuid})),
                        'product_name' : 'LYSHOP'
                    }
                    logger.debug("Sending request payment")
                except Exception as e:
                    logger.error("Error on prepayring payment data")
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
                    
            elif payment_option == commons.PAY_BEFORE_DELIVERY:
                pass

            elif payment_option == commons.PAY_BY_SMS:
                pass 

            elif payment_option == commons.PAY_AT_DELIVERY:
                pass

        else:
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
    try:
        order = Order.objects.get(order_uuid=order_uuid)
    except Order.DoesNotExist as e:
        logger.error(f"checkout_success view call with invalid order uuid \"{order_uuid}\". No order found")
        raise Http404

    if order.payment_option == commons.PAY_AT_ORDER:
        queryset = PaymentRequest.objects.filter(order__order_uuid=order_uuid, customer=request.user)
        if not queryset.exists():
            logger.error(f"checkout_success view call with order uuid \"{order_uuid}\". No Payment request  found")
            raise Http404
        queryset.update(status=commons.ORDER_PAID, payment_status=commons.PAYMENT_PAID)
        payment_request = queryset.first()
        Order.objects.filter(order_uuid=order_uuid).update(status=commons.ORDER_PAID, is_paid=True)
        OrderStatusHistory.objects.create(order=order, order_status=commons.ORDER_PAID, order_ref_id=order.id, changed_by=request.user)

    orders_service.order_clear_cart(request.user)
    flag = orders_service.mark_product_sold(order)
    p_mode = order.payment_method.mode
    if p_mode == commons.ORDER_PAYMENT_CASH:
        tags_template = "tags/checkout_success_cash.html"
    elif p_mode == commons.ORDER_PAYMENT_MOBILE:
        tags_template = "tags/checkout_success_mobile.html"
    elif p_mode == commons.ORDER_PAYMENT_PAY:
        tags_template = "tags/checkout_success_pay.html"
    messages.success(request,"order has been successfully submitted")
    context = {
        'page_title' : page_title,
        'order': order,
        'payment_option': order.payment_option,
        'payment_method': order.payment_method,
        'tags_template' : tags_template
    }
    return render(request, template_name, context)


def checkout_failed(request, order_uuid):
    page_title = _("Checkout failed") + " - " + settings.SITE_NAME
    template_name = "orders/checkout_failed.html"
    order = None
    payment_request = None
    try:
        order = Order.objects.get(order_uuid=order_uuid)
    except Order.DoesNotExist as e:
        logger.error(f"checkout_failed view call with invalid order uuid \"{order_uuid}\". No order found")
        raise Http404
    #queryset = PaymentRequest.objects.filter(request_uuid=request_uuid, order__order_uuid=order_uuid)
    if order.payment_option == commons.PAY_AT_ORDER:
        try:
            payment_request = PaymentRequest.objects.filter(order__order_uuid=order_uuid, customer=request.user).get()
            logger.info(f"Checkout failed : found payment request with order uuid \"{order_uuid}\"")
            PaymentRequest.objects.filter(id=payment_request.id).update(payment_status=commons.PAYMENT_FAILED)
            Order.objects.filter(order_uuid=order_uuid).update(status=commons.ORDER_PAYMENT_FAILED)
            OrderStatusHistory.objects.create(order=order, order_status=commons.ORDER_PAYMENT_FAILED, order_ref_id=order.id, changed_by=request.user)
            orders_service.cancel_order(order)
        except PaymentRequest.DoesNotExist:
            logger.error(f"checkout_failed view call with invalid order uuid \"{order_uuid}\". No order found")
            raise Http404

    context = {
        'page_title' : page_title
    }
    return render(request, template_name, context)


