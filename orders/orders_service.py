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
    order = Order.objects.create(user=user)
    items_queryset = get_user_cartitems(user)
    batch_size = 10
    orderitems = (OrderItem(order=order, product=item.product, quantity=item.quantity, unit_price=item.unit_price,total_price=item.total_price) for item in items_queryset)
    while True:
        batch = list(islice(orderitems, batch_size))
        if not batch:
            break
        OrderItem.objects.bulk_create(batch, batch_size)
    return refresh_order(order)

def request_payment(url=None, **data):
    if not url or not data:
        return None
    
    if not settings.PAY_USERNAME or not settings.PAY_REQUEST_TOKEN:
        logger.warning('PAY:USER or PAY_REQUEST_TOKEN environment variable is not defined.')
        return None
    
    response = requests.post(url, data=data, auth=(settings.PAY_USERNAME, settings.PAY_REQUEST_TOKEN))
    
    if not response:
        logger.error(f"Error on requesting a payment to the url {url} : status code {response.status_code}")
        return None
    return response.json()['token']