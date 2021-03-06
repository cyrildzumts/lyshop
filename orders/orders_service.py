from lyshop import settings, utils
from django.shortcuts import redirect, reverse
from django.db.models import F,Q,Count, Sum, FloatField
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.utils import timezone
from core.tasks import send_mail_task, send_order_mail_task
from cart.models import CartItem, CartModel
from cart import cart_service
from orders import commons
from orders.models import Order, OrderItem,PaymentRequest, OrderStatusHistory, PaymentMethod, OrderPayment, Refund
from orders.forms import PaymentMethodForm
from catalog.models import Product, ProductVariant
from vendors.models import SoldProduct, Balance, BalanceHistory
from shipment import shipment_service
from shipment import constants as SHIPMODE_CONSTANTS
from addressbook import addressbook_service
from itertools import islice
import requests
import json
import logging
import uuid
import datetime
import copy


logger = logging.getLogger(__name__)

SHIPPING_PRICE = 3000
EXPRESS_SHIPPING_PRICE = 5000
# Create Pricing Model in Shipment to simplify shipment pricing tracking

def get_user_cart(user):
    return cart_service.get_cart(user)

def get_user_cartitems(user):
    return cart_service.get_cartitems(user)

def refresh_order(order):
    if order:
        aggregation = OrderItem.objects.filter(order=order).aggregate(count=Sum('quantity'), total=Sum(F('quantity')*F('unit_price'), output_field=FloatField()))
        Order.objects.filter(id=order.id).update(quantity=aggregation['count'], amount=aggregation['total'])
        order.refresh_from_db()
    
    return order

def create_order_from_cart(**kwargs):
    logger.debug("creating order from Cart")
    user = kwargs['user']
    ship_mode = kwargs['ship_mode']
    cart = get_user_cart(user)
    total = 0
    if cart.coupon:
        total = cart.solded_price
    else:
        total = cart.amount
    total += ship_mode.price
    logger.info(f"create_order_from_cart : Total : {total}")
    #order = Order.objects.create(user=user, address=address, coupon=cart.coupon, amount=cart.amount, solded_price=cart.solded_price, quantity=cart.quantity, shipping_price=SHIPPING_PRICE, total=total)
    order_kwargs = {'coupon' : cart.coupon, 'amount' : cart.amount, 'solded_price' : cart.solded_price, 'quantity' : cart.quantity, 'shipping_price' : ship_mode.price, 'total' : total}
    order_kwargs.update(kwargs)
    order = Order.objects.create(**order_kwargs)
    OrderStatusHistory.objects.create(order=order, order_status=order.status, order_ref_id=order.id, changed_by=user)
    logger.debug("order instance created")
    items_queryset = get_user_cartitems(user)
    logger.debug("got cartitems queryset")
    batch_size = 10
    logger.debug("preparing orderitems from CartItems")
    orderitems = None
    product_update_list = items_queryset.values_list('product', 'product__quantity', 'quantity')
    try:
        orderitems = (OrderItem(order=order, product=item.product, quantity=item.quantity,promotion_price=item.promotion_price, unit_price=item.original_price,total_price=item.item_total_price) for item in items_queryset)
    except Exception as e:
        logger.error("error on preparing orderitems from CartItems")
        logger.exception(e)
    logger.debug("orderitems prepared from CartItems")

    if orderitems:
        while True:
            batch = list(islice(orderitems, batch_size))
            if not batch:
                break
            OrderItem.objects.bulk_create(batch, batch_size)
    for pk, available_quantity, quantity in product_update_list:
        ProductVariant.objects.filter(pk=pk).update(quantity=F('quantity') - quantity, is_active=(available_quantity > quantity))
        Product.objects.filter(variants__in=[pk]).update(quantity=F('quantity') - quantity)
    logger.debug("Order created from Cart")
    return order

#TODO Filter user high failed delivery rate
def order_pay_at_delivery(user, data):
    result = {}
    if  not isinstance(user, User) or not isinstance(data, dict):
        logger.warn(f"order_pay_at_delivery : User or data has a wrong type. Expecting user type to be User but got a {type(user)} instead ")
        logger.warn(f"order_pay_at_delivery : User or data has a wrong type. Expecting data type to be dict or a descendant of a dict but got a {type(data)} instead ")
        return result
    logger.info("Processing order_pay_at_delivery")
    p_method = data.get(commons.PAYMENT_METHOD_FIELD)
    if p_method.mode != commons.ORDER_PAYMENT_CASH:
        logger.warn(f"order_pay_at_delivery : wrong payment method. current payment method : {p_method}; Expected payment method {commons.ORDER_PAYMENT_CASH}")
        result = {
            'success': False,
            'msg' : "Expected CASH Payment method"
        }
    else:
        order = create_order_from_cart(**{'user': user,'payment_option': commons.PAY_AT_DELIVERY, 'address':  data.get(commons.SHIPPING_ADDRESS_FIELD), 'payment_method': p_method, commons.SHIP_MODE_FIELD : data.get(commons.SHIP_MODE_FIELD) })
        redirect_success_url = reverse('orders:checkout-success', kwargs={'order_uuid': order.order_uuid})
        redirect_failed_url = reverse('orders:checkout-failed', kwargs={'order_uuid': order.order_uuid})
        result = {
            'success': True,
            'order' : order,
            commons.KEY_REDIRECT_SUCCESS_URL: redirect_success_url,
            commons.KEY_REDIRECT_FAILED_URL: redirect_failed_url
        }
    return result
    

def order_pay_at_order(user, data):
    
    result = {}
    if  not isinstance(user, User) or not isinstance(data, dict):
        logger.warn(f"order_pay_at_order : User or data has a wrong type. Expecting user type to be User but got a {type(user)} instead ")
        logger.warn(f"order_pay_at_order : User or data has a wrong type. Expecting data type to be dict or a descendant of a dict but got a {type(data)} instead ")
        return result

    logger.info("Processing order_pay_at_order")
    request = data['request']
    if commons.PAYMENT_METHOD_FIELD not in data:
        logger.warn(f"order_pay_at_order : Invalid data : PAYMENT_METHOD_FIELD(\"{commons.PAYMENT_METHOD_FIELD}\") not found in data.")
        return result
    
    address = data.get(commons.SHIPPING_ADDRESS_FIELD)
    order = create_order_from_cart(**{'user': user, 'address' : address, 'payment_option': data.get(commons.PAYMENT_OPTION_FIELD), 'payment_method': data.get(commons.PAYMENT_METHOD_FIELD), commons.SHIP_MODE_FIELD : data.get(commons.SHIP_MODE_FIELD)})
    redirect_success_url = reverse('orders:checkout-success', kwargs={'order_uuid': order.order_uuid})
    redirect_failed_url = reverse('orders:checkout-failed', kwargs={'order_uuid': order.order_uuid})
    result = {
        'success': False,
        commons.KEY_REDIRECT_SUCCESS_URL: redirect_success_url,
        commons.KEY_REDIRECT_FAILED_URL: redirect_failed_url
    }
    try:
        payment_data = {
            'requester_name': settings.PAY_USERNAME,
            'amount': order.total,
            'customer_name': user.get_full_name(),
            'quantity': order.quantity,
            'description': settings.PAY_REQUEST_DESCRIPTION,
            'country' : address.country,
            'redirect_success_url': request.build_absolute_uri(redirect_success_url),
            'redirect_failed_url': request.build_absolute_uri(redirect_failed_url),
            'product_name' : 'LYSHOP'
        }
    except Exception as e:
        logger.error("Error on prepayring payment data")
        logger.exception(e)
        return result
    
    response = request_payment(payment_data)
    if response:
        response_json = response.json()
        logger.debug(f"request payment succeed for order {order.order_ref_number}")
        payment_data['token'] = response_json['token']
        payment_data['pay_url'] = response_json['url']
        payment_data['order'] = order
        payment_data['customer'] = user
        payment_data['verification_code'] = response_json['verification_code']
        try:
            payment_request = PaymentRequest.objects.create(**payment_data)
            result['success'] = True
            result[commons.KEY_REDIRECT_PAYMENT_URL] = reverse('orders:checkout-redirect-payment', kwargs={'request_uuid' : payment_request.request_uuid})
            result['order'] = order
            return result
        except Exception as e:
            logger.error(f"Error on creating PaymentRequest for order {order.order_ref_number}")
            logger.exception(e)
        

    logger.debug("order failed")
    return result
    

def order_pay_before_delivery(user, data):
    result = {}
    if  not isinstance(user, User) or not isinstance(data, dict):
        logger.warn(f"order_pay_before_delivery : User or data has a wrong type. Expecting user type to be User but got a {type(user)} instead ")
        logger.warn(f"order_pay_before_delivery : User or data has a wrong type. Expecting data type to be dict or a descendant of a dict but got a {type(data)} instead ")
        return result
    logger.info("Processing order_pay_before_delivery")

    order = create_order_from_cart(**{'user': user,'payment_option': commons.PAY_BEFORE_DELIVERY, 'address':  data.get(commons.SHIPPING_ADDRESS_FIELD), 'payment_method': data.get(commons.PAYMENT_METHOD_FIELD), commons.SHIP_MODE_FIELD : data.get(commons.SHIP_MODE_FIELD)})
    redirect_success_url = reverse('orders:checkout-success', kwargs={'order_uuid': order.order_uuid})
    redirect_failed_url = reverse('orders:checkout-failed', kwargs={'order_uuid': order.order_uuid})
    result = {
        'success': True,
        'order' : order,
        commons.KEY_REDIRECT_SUCCESS_URL: redirect_success_url,
        commons.KEY_REDIRECT_FAILED_URL: redirect_failed_url
    }
    return result

    

def process_order(user, request):
    postdata = utils.get_postdata(request)
    address = None
    payment_option = None
    payment_method = None
    result = {'success' : False}
    if  not isinstance(user, User) or not isinstance(postdata, dict):
        logger.warn(f"process_order : User or postdata has a wrong type. Expecting user type to be User but got a {type(user)} instead ")
        logger.warn(f"process_order : User or postdata has a wrong type. Expecting postdata type to be dict or a descendant of a dict but got a {type(postdata)} instead ")
        return result
    
    if commons.SHIP_MODE_FIELD not in postdata:
        logger.warn(f"process_order : SHIP_MODE_FIELD {commons.SHIP_MODE_FIELD} missing")
        return result

    ship_mode = shipment_service.get_ship_mode_from_id(int(postdata.get(commons.SHIP_MODE_FIELD)))

    if commons.PAYMENT_OPTION_FIELD not in postdata:
        logger.warn(f"process_order : PAYMENT_OPTION_FIELD {commons.PAYMENT_OPTION_FIELD} missing")
        return result

    payment_option = int(postdata.get(commons.PAYMENT_OPTION_FIELD))

    if commons.PAYMENT_METHOD_FIELD not in postdata:
        logger.warn(f"process_order : PAYMENT_METHOD_FIELD \"{commons.PAYMENT_METHOD_FIELD}\" missing")
        return result
    
    try:
        payment_method = PaymentMethod.objects.get(id=int(postdata.get(commons.PAYMENT_METHOD_FIELD)))
    except ObjectDoesNotExist as e:
        logger.warn(f"process_order : no payment_method found with id \"{postdata.get(commons.PAYMENT_METHOD_FIELD)}\" mode = ORDER_PAYMENT_PAY which is \"{commons.ORDER_PAYMENT_PAY}\"")
        logger.exception(e)
        return result

    if commons.SHIPPING_ADDRESS_FIELD not in postdata and ship_mode.mode not in shipment_service.constants.IN_STORE_PICK_MODE:
        logger.warn(f"process_order : SHIPPING_ADDRESS_FIELD \"{commons.SHIPPING_ADDRESS_FIELD}\" missing for the selected shipping mode {ship_mode}")
        return result
    
    if ship_mode.mode not in shipment_service.constants.IN_STORE_PICK_MODE:
        try:
            addr_pk = int(postdata.get(commons.SHIPPING_ADDRESS_FIELD))
            address = addressbook_service.get_address(addr_pk)
        except TypeError as e:
            logger.warning("error while reading address pk from query parameter", e)
            return result
    if not address:
        logger.warn(f"process_order : no address found with id \"{postdata.get(commons.SHIPPING_ADDRESS_FIELD)}\". shipping mode {ship_mode}")
        #return result

    
    data = {'postdata': postdata,'request': request, commons.PAYMENT_METHOD_FIELD : payment_method, commons.SHIP_MODE_FIELD : ship_mode ,commons.SHIPPING_ADDRESS_FIELD : address, commons.PAYMENT_OPTION_FIELD : payment_option}
    if payment_option == commons.PAY_BEFORE_DELIVERY:
        result = order_pay_before_delivery(user, data)
    elif payment_option == commons.PAY_AT_DELIVERY:
        result = order_pay_at_delivery(user, data)
    elif payment_option == commons.PAY_AT_ORDER:
        result = order_pay_at_order(user, data)

    return result
    
def restore_product(order):
    item_queryset = order.order_items.all()
    product_update_list = item_queryset.values_list('product', 'quantity')
    logger.debug(f"restore_product {product_update_list}")
    for pk, quantity in product_update_list:
        ProductVariant.objects.filter(pk=pk).update(quantity=F('quantity') + quantity, is_active=True)
        Product.objects.filter(variants__in=[pk]).update(quantity=F('quantity') + quantity)

def cancel_order(order, request_user=None):
    if  not isinstance(order, Order):
        return False
    
    if not is_cancelable(order):
        return False

    Order.objects.filter(pk=order.pk).update(is_closed=True, is_active=False, status=commons.ORDER_CANCELED, last_changed_by=request_user)
    restore_product(order)
    refund_order(order)
    return True


def clean_unpaid_orders():
    request_user = User.objects.get(username='admin')
    payment_due_date = timezone.now() - datetime.timedelta(commons.ORDER_PAID_DAY_DELAY)
    queryset = Order.objects.filter(status=commons.ORDER_SUBMITTED, is_paid=False, created_at__lt=payment_due_date)
    orders_count = queryset.count()
    logger.info(f"Clean unpaid orders : updating unpaid orders")
    for order in queryset:
        logger.info(f"Cancelling order {order}")
        if cancel_order(order, request_user):
            send_order_mail_confirmation(order=order, cancellation=True)
    
    logger.info(f"Clean unpaid orders : updated {orders_count} unpaid orders")
    


def order_clear_cart(user):
    logger.debug("Order - Clearing Cart Items")
    return cart_service.clear_cart(user)


def get_sold_products(seller):
    if  not isinstance(seller, User):
        return None
    return OrderItem.objects.filter(product__product__sold_by=seller, order__is_paid=True)


def mark_product_sold(order):
    if  not isinstance(order, Order) or order.vendor_balance_updated:
        return False
    order_items = order.order_items.select_related().all()
    sold_products_data = [{'order': order,'customer':order.user, 'seller':item.product.product.sold_by, 'product':item.product, 'quantity': item.quantity, 'promotion_price':item.promotion_price, 'unit_price':item.unit_price, 'total_price':item.total_price} for item in order_items]
    SoldProduct.objects.bulk_create([SoldProduct(**data) for data in sold_products_data])
    return True



def mark_order_paid(order):
    if  not isinstance(order, Order) or order.is_paid:
        return False
    order_items = order.order_items.select_related().all()
    sold_products_data = [{'customer':order.user, 'seller':item.product.product.sold_by, 'product':item.product, 'quantity': item.quantity, 'promotion_price':item.promotion_price, 'unit_price':item.unit_price, 'total_price':item.total_price} for item in order_items]
    balance_updates = ((p['seller'], p['total_price'], p['customer'], p['seller'].balance) for p in sold_products_data)
    with transaction.atomic():
        for s, total, customer, balance in balance_updates:
            balance.refresh_from_db()
            Balance.objects.filter(user=s).update(balance=F('balance') + total)
            BalanceHistory.objects.create(balance=balance, balance_ref_id=balance.pk, current_amount=balance.balance,balance_amount=total, sender=customer, receiver=s)
        Order.objects.filter(id=order.id).update(vendor_balance_updated=True, is_paid=True, status=commons.ORDER_PAID)
    
    payment_mode = order.payment_method.mode
    if not payment_mode == commons.ORDER_PAYMENT_PAY:
        OrderPayment.objects.create(amount=order.total, sender=order.user, order=order, payment_mode=payment_mode, verification_code="N/A")
    
    return True


def request_payment(data=None):
    if not settings.LYSHOP_PAY_REQUEST_URL or not settings.PAY_USERNAME or not settings.PAY_REQUEST_TOKEN:
        logger.warning('PAY:USER or PAY_REQUEST_TOKEN environment variable is not defined.')
        return None
    url = settings.LYSHOP_PAY_REQUEST_URL
    headers={'Authorization': f"Token {settings.PAY_REQUEST_TOKEN}"}
    logger.debug(f'Sending payment request to url {url}')
    response = None
    try:
        response = requests.post(url, data=data, headers=headers)
        logger.debug(f'payment request response : {response}')
        if not response:
            logger.error(f"Error on requesting a payment to the url {url} : status code {response.status_code} - error : {response}")
    except Exception as e:
        logger.error(f"Error on sending Payment request at url {url}")
        logger.exception(e)
    return response


def is_marked_for_shipment(order):
    if not isinstance(order, Order):
        logger.error("Type Error : order not of Order type")
        raise TypeError("Type Error : order argument not of type Order.")
    return shipment_service.shipment_for_order_exists(order)


def is_cancelable(order):
    if not isinstance(order, Order):
        logger.error("Type Error : order not of Order type")
        raise TypeError("Type Error : order argument not of type Order.")
    
    flag = not is_marked_for_shipment(order) and (order.status == commons.ORDER_SUBMITTED or order.status == commons.ORDER_PAID)
    flag = flag and not order.status == commons.ORDER_CANCELED
    return flag




def can_be_shipped(order):
    '''
    An order can be shipped only when it has a status of
    commons.ORDER_PAID or the payment_order for the order 
    is set to commons.PAY_AT_DELIVERY.
    '''
    if not isinstance(order, Order):
        logger.error("Type Error : order not of Order type")
        raise TypeError("Type Error : order argument not of type Order.")
    
    return order.status == commons.ORDER_READY_FOR_SHIPMENT and not is_marked_for_shipment(order)
        




def add_shipment(order):
    '''
    add_shipment this method marks an order as ready
    for shipment.
    An order can be added for shipment when it has not been already marked
    for shipment and can be shipped.
    '''
    if not isinstance(order, Order):
        logger.error("Type Error : order not of Order type")
        return False
    

    if is_marked_for_shipment(order):
        logger.error(f"Order {order.id} has already been be added for shipment.")
        return False

    elif can_be_shipped(order):
            return shipment_service.add_shipment(order)
    else:
        logger.error(f"Order {order.id} can not be added for shipment. Order has not been already paid or customer did not choose to pay at delivery")

    return False


#TODO
def order_can_be_deleted(order):
    if not isinstance(order, Order):
        logger.error("Type Error : order not of Order type")
        raise TypeError("Type Error : order argument not of type Order.")

    return False


def get_order_shipment(order):
    if not isinstance(order, Order):
        logger.error("Type Error : order not of Order type")
        raise TypeError("Type Error : order argument not of type Order.")
    shipment = None
    return shipment_service.find_order_shipment(order)


def is_refundable(order):
    if not isinstance(order, Order):
        logger.error("Type Error : order not of Order type")
        raise TypeError("Type Error : order argument not of type Order.")

    if not order.is_paid:
        return False
    #status = Q(status=commons.REFUND_PAID) | Q(status=commons.REFUND_PENDING) | Q(status=commons.REFUND_ACCEPTED) | Q(status=commons.REFUND_CANCELLED)
    exists = Refund.objects.filter(order=order).exists()
    return not exists

## TODO
def refund_order(order):
    if not isinstance(order, Order):
        logger.error("Type Error : order not of Order type")
        raise TypeError("Type Error : order argument not of type Order.")
        
    if not is_refundable(order):
        msg = "Refund Order - Order is not paid. Refund not possible"
        logger.warning(msg)
        return False, msg

    order_payment = OrderPayment.objects.filter(order=order).first()
    Refund.objects.create(amount=order.amount, user=order.user, payment=order_payment, order=order)
    return True, "Refund order submitted"
    

def accept_refund(refund_uuid, request_user):
    refund = Refund.objects.get(refund_uuid=refund_uuid)
    order = refund.order
    if refund.status != commons.REFUND_PENDING:
        logger.warning("Refund was already processing. Only prefund in pending statte can accepted")
        #return False
    
    if SoldProduct.objects.filter(order=order).exists():
        items_queryset = order.order_items.select_related().all()
        product_update_list = tuple(items_queryset.values_list('product', 'quantity'))
        Order.objects.filter(pk=order.pk).update(is_closed=True, is_active=False, status=commons.ORDER_REFUND, last_changed_by=request_user)
        for pk, quantity in product_update_list:
            ProductVariant.objects.filter(pk=pk).update(quantity=F('quantity') + quantity, is_active=True)
            Product.objects.filter(variants__in=[pk]).update(quantity=F('quantity') + quantity, is_active=True)
        SoldProduct.objects.filter(order=order).delete()
    return Refund.objects.filter(refund_uuid=refund_uuid).update(status=commons.REFUND_ACCEPTED)

def pay_refund(refund_uuid):
    refund = Refund.objects.get(refund_uuid=refund_uuid)
    order = refund.order
    order_items = order.order_items.select_related().all()
    sold_products_data = [{'customer':order.user, 'seller':item.product.product.sold_by, 'product':item.product, 'quantity': item.quantity, 'promotion_price':item.promotion_price, 'unit_price':item.unit_price, 'total_price':item.total_price} for item in order_items]
    balance_updates = ((p['seller'], p['total_price'], p['customer'], p['seller'].balance) for p in sold_products_data)
    with transaction.atomic():
        for s, total, customer, balance in balance_updates:
            balance.refresh_from_db()
            Balance.objects.filter(user=s).update(balance=F('balance') - total)
            BalanceHistory.objects.create(balance=balance, balance_ref_id=balance.pk, current_amount=balance.balance,balance_amount=-total, sender=customer, receiver=s)
        Order.objects.filter(id=order.id).update(vendor_balance_updated=True, is_paid=True, status=commons.ORDER_REFUNDED)
    Refund.objects.filter(refund_uuid=refund_uuid).update(status=commons.REFUND_PAID)
    return True

def get_payment_method(name=""):
    if isinstance(name, str) and len(name) > 0:
        try:
            return PaymentMethod.objects.get(name=name)
        except PaymentMethod.DoesNotExist as e:
            logger.warn(f'get_payment_method: No PaymentMethod found with name \"{name}\"')
    return None

def get_payment_methods(filter_active=False):
    if filter_active:
        qs = PaymentMethod.objects.filter(is_active=True)
    else:
        qs = PaymentMethod.objects.all()
    return qs


def create_payment_method(postdata):
    form = PaymentMethodForm(postdata)
    if form.is_valid():
        payment_method = form.save()
        logger.info(f'Created new PaymentMethod {payment_method}')
        return payment_method, True
    else:
        logger.warn(f'PaymentMethodForm invalid. Errors : {form.errors}')
        return None, False


def update_payment_method(postdata, payment_method):
    if not isinstance(payment_method, PaymentMethod):
        payment_method, False
    form = PaymentMethodForm(postdata, instance=payment_method)
    if form.is_valid():
        payment_method = form.save()
        logger.info(f'Updated PaymentMethod {payment_method}')
        return payment_method, True
    else:
        logger.warn(f'PaymentMethodForm invalid. Errors : {form.errors}')
        return payment_method, False




def send_order_mail_confirmation(order, cancellation=False):
    if cancellation:
        TEMPLATE_NAME = commons.ORDER_CANCEL_CONFIRMATION_MAIL_TEMPLATE
        TEMPLATE_TITLE = commons.ORDER_CANCEL_CONFIRMATION_MAIL_TITLE
    else:
        TEMPLATE_NAME = commons.ORDER_CONFIRMATION_MAIL_TEMPLATE
        TEMPLATE_TITLE = commons.ORDER_CONFIRMATION_MAIL_TITLE
    

    order_status_key, order_status_value = commons.get_order_status_name(order.status)
    payment_option_key, payment_option_value = commons.get_payment_option_name(order.payment_option)
    address = None
    ship_mode = None
    if order.ship_mode.mode not in SHIPMODE_CONSTANTS.IN_STORE_PICK_MODE:
        address = order.address.to_str()
    else:
        address = order.ship_mode.display_name
        ship_mode = address

    email_context = {
                'order' : order.pk,
                'template_name' : TEMPLATE_NAME,
                'title': TEMPLATE_TITLE,
                'recipient_email': order.user.email,
                'user': order.user.pk,
                'context' : {
                    'SITE_NAME': settings.SITE_NAME,
                    'SITE_HOST': settings.SITE_HOST,
                    'FULL_NAME': order.user.get_full_name(),
                    'AMOUNT': order.amount,
                    'SHIPPING_PRICE': order.ship_mode.price,
                    'ADDRESS' : address,
                    'SHIP_MODE': ship_mode,
                    'COUPON' : '',
                    'PAYMENT_OPTION' : payment_option_value,
                    'ORDER_STATUS': order_status_value,
                    'CURRENCY': settings.CURRENCY,
                    'TOTAL' : order.total,
                    'REFERENCE_NUMBER' : order.order_ref_number
                }
            }
    send_order_mail_task.apply_async(
        args=[email_context],
        queue=settings.CELERY_OUTGOING_MAIL_EXCHANGE,
        routing_key=settings.CELERY_OUTGOING_MAIL_ROUTING_KEY
    )

    admin_email_context = copy.deepcopy(email_context)
    admin_email_context['recipient_email'] = settings.ADMIN_EXTERNAL_EMAIL
    send_mail_task.apply_async(
        args=[admin_email_context],
        queue=settings.CELERY_OUTGOING_MAIL_QUEUE,
        routing_key=settings.CELERY_OUTGOING_MAIL_ROUTING_KEY
    )



def send_shipment_mail_confirmation(order):
    email_context = {
                'order_id' : order.pk,
                'template_name' : commons.SHIPMENT_CONFIRMATION_MAIL_TEMPLATE,
                'title': commons.SHIPMENT_CONFIRMATION_MAIL_TITLE,
                'recipient_email': order.user.email
            }
    send_mail_task.apply_async(
        args=[email_context],
        queue=settings.CELERY_OUTGOING_MAIL_EXCHANGE,
        routing_key=settings.CELERY_OUTGOING_MAIL_ROUTING_KEY
    )

    admin_email_context = copy.deepcopy(email_context)
    admin_email_context['recipient_email'] = settings.ADMIN_EXTERNAL_EMAIL
    send_mail_task.apply_async(
        args=[admin_email_context],
        queue=settings.CELERY_OUTGOING_MAIL_QUEUE,
        routing_key=settings.CELERY_OUTGOING_MAIL_ROUTING_KEY
    )