from lyshop import settings
from django.db.models import F,Q,Count, Sum, FloatField
from cart.models import CartItem, CartModel
from cart import cart_service
from orders.models import Order, OrderItem, Address, PaymentRequest
from itertools import islice
import requests
import json
import logging
import uuid


logger = logging.getLogger(__name__)


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
    order = Order.objects.create(user=user)
    logger.debug("order instance created")
    items_queryset = get_user_cartitems(user)
    logger.debug("got cartitems queryset")
    batch_size = 10
    logger.debug("preparing orderitems from CartItems")
    orderitems = None
    try:
        orderitems = (OrderItem(order=order, product=item.product, quantity=item.quantity, unit_price=item.unit_price,total_price=item.total_price) for item in items_queryset)
        batch_size = len(orderitems)
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
    return refresh_order(order)


def order_clear_cart(user):
    return cart_service.clear_cart(user)


def request_payment(data=None):
    if not settings.PAY_REQUEST_URL or not settings.PAY_USERNAME or not settings.PAY_REQUEST_TOKEN:
        logger.warning('PAY:USER or PAY_REQUEST_TOKEN environment variable is not defined.')
        return None
    url = settings.PAY_REQUEST_URL
    headers={'Authorization': f"Token {settings.PAY_REQUEST_TOKEN}"}
    logger.debug('Sending payment request')
    response = requests.post(url, data=data, headers=headers)
    logger.debug(f'payment request response : {response}')
    if not response:
        logger.error(f"Error on requesting a payment to the url {url} : status code {response.status_code} - error : {response.error}")
        return None
    return response.json()['token']