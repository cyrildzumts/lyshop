from lyshop import settings, utils
from django.db.models import F,Q,Count, Sum, FloatField
from django.db import transaction
from django.contrib.auth.models import User
from cart.models import CartItem, CartModel
from cart import cart_service
from orders import commons
from orders.models import Order, OrderItem, Address, PaymentRequest, OrderStatusHistory
from catalog.models import Product, ProductVariant
from vendors.models import SoldProduct, Balance, BalanceHistory
from shipment import shipment_service
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
        ProductVariant.objects.filter(pk=p).update(quantity=F('quantity') - quantity, is_active=(available_quantity > quantity))
    logger.debug("Order created from Cart")
    return order



def cancel_order(order, request_user=None):
    if  not isinstance(order, Order):
        return False
    
    if not is_cancelable(order):
        return False
    items_queryset = order.order_items.select_related().all()
    product_update_list = tuple(items_queryset.values_list('product', 'quantity'))
    Order.objects.filter(pk=order.pk).update(is_closed=True, is_active=False, status=commons.ORDER_CANCELED, last_changed_by=request_user)
    ##TODO Send the money back to the user
    for pk, quantity in product_update_list:
        ProductVariant.objects.filter(pk=pk).update(quantity=F('quantity') + quantity, is_active=True)
    
    return True



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
    sold_products = [SoldProduct(customer=order.user, seller=item.product.product.sold_by, product=item.product, quantity=item.quantity, promotion_price=item.promotion_price, unit_price=item.unit_price, total_price=item.total_price) for item in order_items]
    
    balance_updates = ((p.seller, p.total_price, p.customer, p.seller.balance) for p in sold_products)
    with transaction.atomic():
        for s, total, customer, balance in balance_updates:
            balance.refresh_from_db()
            Balance.objects.filter(user=s).update(balance=F('balance') + total)
            BalanceHistory.objects.create(balance=balance, balance_ref_id=balance.pk, current_amount=balance.balance,balance_amount=total, sender=customer, receiver=s)
        Order.objects.filter(id=order.id).update(vendor_balance_updated=True)
    
    batch_size = 100
    while True:
        batch = list(islice(sold_products, batch_size))
        if not batch:
            break
        SoldProduct.objects.bulk_create(batch, batch_size, ignore_conflicts=True)

    
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
    
    flag = not is_marked_for_shipment(order) and (order.status == commons.ORDER_SUBMITTED or order.payment_option == commons.ORDER_PAID)
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
    
    return order.status == commons.ORDER_PAID or order.payment_option == commons.PAY_AT_DELIVERY
        




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



def get_order_shipment(order):
    if not isinstance(order, Order):
        logger.error("Type Error : order not of Order type")
        raise TypeError("Type Error : order argument not of type Order.")
    shipment = None
    return shipment_service.find_order_shipment(order)