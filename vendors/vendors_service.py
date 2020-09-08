from catalog.models import Product, ProductVariant
from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F,Q,Count, Sum, FloatField
from django.db import transaction
from accounts.models import Account
from vendors.models import SoldProduct, Balance, BalanceHistory
from orders import orders_service
from orders.models import Order, OrderItem
from vendors import constants as Constants
from datetime import date as Date, datetime as DateTime
from payment.models import Payment
from itertools import islice

import json
import logging
import uuid


logger = logging.getLogger(__name__)

def is_vendor(user=None):
    return isinstance(user, User) and user.groups.filter(name=Constants.VENDOR_GROUP).exists()

def can_have_balance(user):
    return isinstance(user, User) and user.groups.filter(name=Constants.FEE_GROUP).exists()


def get_vendor_balance(user):
    if not isinstance(user, User) or not is_vendor(user):
        return None
    balance = None
    try:
        balance = Balance.objects.get(user=user)
    except ObjectDoesNotExist as e:
        pass
    return balance

def get_vendor_home_variable(user):
    if not isinstance(user, User) or not is_vendor(user):
        return {}
    number_sold_products = SoldProduct.objects.filter(seller=user).aggregate(count=Sum('quantity')).get('count', 0)
    product_count  = user.sold_products.aggregate(count=Sum('quantity')).get('count', 0)
    return {'product_count' : product_count, 'number_sold_products' : number_sold_products}


def get_next_payment_date(user):
    today = DateTime.now()
    next_payment_date = None
    if today.day < Constants.VENDOR_PAYMENT_DAY:
        next_payment_date = Date(today.year, today.month, Constants.VENDOR_PAYMENT_DAY)

    elif today.day == Constants.VENDOR_PAYMENT_DAY:
        next_payment_date = Date(today.year, today.month, today.day)
    if today.day > Constants.VENDOR_PAYMENT_DAY:
        month  = 1
        year = today.year
        if today.month < 12:
            montth = today.month + 1
            year = today.year 
        else:
            year = today.year + 1
            month = 1
        next_payment_date = Date(year, month, Constants.VENDOR_PAYMENT_DAY)
    
    return next_payment_date


def get_vendor_payments(seller):
    if not isinstance(seller, User) or not is_vendor(seller):
        logger.warn(f"get_vendor_payment : The given user is not a vendor")
        return Payment.objects.none()
    
    return Payment.objects.filter(seller=seller).order_by('-created_at')


def reset_vendor(seller):
    if not isinstance(seller, User) or not is_vendor(seller):
        logger.warn(f"Reseting User balance not processed. The given user is not a vendor")
        return False

    #order_queryset = Order.objects.filter(is_paid=True, vendor_balance_updated=True)
    #if not order_queryset.exists():
    #    logger.warn(f"Reseting Vendor {seller.username} not processed. No valid order found")
    #    return False
    
    logger.warn(f"Reseting Vendor {seller.username} started")
    order_items_queryset = OrderItem.objects.filter(product__product__sold_by=seller)
    if not order_items_queryset.exists():
        logger.warn(f"Reseting Vendor {seller.username} not processed. No valid order items found")
        return False
    Balance.objects.filter(user=seller).update(balance=0)
    BalanceHistory.objects.filter(receiver=seller).delete()
    SoldProduct.objects.filter(seller=seller).delete()
    Order.objects.filter(order_items__in=order_items_queryset).update(vendor_balance_updated=False)
    logger.warn(f"Reseting Vendor {seller.username} finished")
    return True

def update_sold_product(seller):
    if not isinstance(seller, User) or not is_vendor(seller):
        return False

    reset_vendor(seller)

    order_queryset = Order.objects.filter(is_paid=True, vendor_balance_updated=False)
    if not order_queryset.exists():
        return False

    logger.info("update_sold_product(): found orders to update")
    order_items_queryset = OrderItem.objects.filter(product__product__sold_by=seller, order__in=order_queryset)
    order_items_iter = OrderItem.objects.filter(product__product__sold_by=seller, order__in=order_queryset).iterator()
    #balance_aggregate = order_items_queryset.aggregate(balance=Sum('total_price', output_field=FloatField()))
    #balance = balance_aggregate.get('balance', 0.0)
    #Balance.objects.filter(user=seller).update(balance=F('balance') + balance)
    #TODO BalanceHistory must reflect the balance changes by each customer buy
    #BalanceHistory.objects.create(balance=seller.balance, balance_ref_id=seller.balance.pk, balance_amount=seller.balance.balance + balance, receiver=seller)
    #batch_size = 20
    #sold_products = [SoldProduct(seller=seller, customer=item.order.user, product=item.product, quantity=item.quantity, unit_price=item.unit_price, total_price=item.total_price) for item in order_items_iter]
    
    logger.info(f"update_sold_product() : Starting updating vendor \"{seller.username}\" ")
    #sold_products = []
    balance_updates = ((p.total_price, p.order.user, item) for p in order_items_iter)
    current_balance = seller.balance.balance
    with transaction.atomic():
        for item in order_items_iter:
            customer = item.order.user
            SoldProduct.objects.create(seller=seller, customer=customer, product=item.product, quantity=item.quantity, unit_price=item.unit_price, total_price=item.total_price)
            Balance.objects.filter(user=seller).update(balance=F('balance') + item.total_price)
            BalanceHistory.objects.create(balance=seller.balance, balance_ref_id=seller.balance.pk, current_amount=current_balance, balance_amount=item.total_price, sender=customer, receiver=seller)
            current_balance += item.total_price

    logger.info(f"update_sold_product() : Vendor \"{seller.username}\" uddated  ")

    '''
    while True:
        batch = list(islice(sold_products, batch_size))
        if not batch:
            break
        SoldProduct.objects.bulk_create(batch, batch_size, ignore_conflicts=True)
    '''
    Order.objects.filter(order_items__in=order_items_queryset).update(vendor_balance_updated=True)
    logger.info(f"update_sold_product() : [OK] Finished updating Vendor \"{seller.username}\"")
    return True


def update_balance_history(seller):
    if not isinstance(seller, User) or not is_vendor(seller):
        return False

    order_queryset = Order.objects.filter(is_paid=True, vendor_balance_updated=False)
    if not order_queryset.exists():
        return False
    order_items_queryset = OrderItem.objects.filter(product__product__sold_by=seller, order__in=order_queryset)
    #balance_aggregate = order_items_queryset.aggregate(balance=Sum('total_price', output_field=FloatField()))
    
    batch_size = 20
    sold_products = [SoldProduct(seller=seller, customer=item.order.user, product=item.product, quantity=item.quantity, unit_price=item.unit_price, total_price=item.total_price) for item in order_items_queryset]
    
    balance_updates = ((p.seller, p.total_price, p.customer) for p in sold_products)
    with transaction.atomic():
        for p_seller, total, customer in balance_updates:
            BalanceHistory.objects.create(balance=p_seller.balance, balance_ref_id=p_seller.balance.pk, balance_amount=total, sender=customer, receiver=p_seller)
        Order.objects.filter(id=order.id).update(vendor_balance_updated=True)
    
    return True


def get_pending_payment(user):
    pass
