from lyshop import settings
from django.db.models import F,Q,Count, Sum, FloatField
from cart.models import CartItem, CartModel
from cart import cart_service
from orders.models import Order, OrderItem, Address, PaymentRequest
from shipment.models import Shipment
from itertools import islice
import requests
import json
import logging
import uuid


logger = logging.getLogger(__name__)

SHIPPING_PRICE = 3000
EXPRESS_SHIPPING_PRICE = 5000

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

def create_order_from_cart(user):
    logger.debug("creating order from Cart")
    cart = get_user_cart(user)
    total = 0
    if cart.coupon:
        total = cart.solded_price + SHIPPING_PRICE
    else:
        total = cart.amount + SHIPPING_PRICE
    order = Order.objects.create(user=user, coupon=cart.coupon, amount=cart.amount, solded_price=cart.solded_price, quantity=cart.quantity, shipping_price=SHIPPING_PRICE, total=total)
    logger.debug("order instance created")
    items_queryset = get_user_cartitems(user)
    logger.debug("got cartitems queryset")
    batch_size = 10
    logger.debug("preparing orderitems from CartItems")
    orderitems = None
    try:
        orderitems = (OrderItem(order=order, product=item.product, quantity=item.quantity, unit_price=item.unit_price,total_price=item.total_price) for item in items_queryset)
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
    logger.debug("Order created from Cart")
    return order


def order_clear_cart(user):
    logger.debug("Order - Clearing Cart Items")
    return cart_service.clear_cart(user)


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


def add_shipment(order):
    if not isinstance(order, Order):
        logger.error("Type Error : order not of Order type")
        return False
    data = {
        'shipment_number' : 12,
        'customer': order.user,
        'order' : order,
        'price' : order.shipping_price,
        'company': "LYSHOP"
    }
    shipment, created = Shipment.objects.create(**data)
    if created:
        logger.info(f"Shipment created for order {order.pk}")
    else:
        logger.info(f"Shipment could not be created for order {order.pk}")
    return created

def is_marked_for_shipment(order):
    if not isinstance(order, Order):
        logger.error("Type Error : order not of Order type")
        return False
    return Shipment.objects.filter(order=order).exists()

def get_order_shipment(order):
    if not isinstance(order, Order):
        logger.error("Type Error : order not of Order type")
        return False
    shipment = None
    try:
        shipment = Shipment.objects.get(order=order)
    except Shipment.DoesNotExist as e:
        pass
    return shipment