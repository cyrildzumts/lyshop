from catalog.models import Product, ProductVariant
from django.contrib.auth.models import User, Group
from django.db.models import F,Q,Count, Sum, FloatField
from accounts.models import Account
from vendors.models import SoldProduct, Balance, BalanceHistory
from orders import orders_service
from orders.models import Order, OrderItem
from vendors import constants as Constants
from datetime import date as Date, datetime as DateTime
from itertools import islice

def is_vendor(user=None):
    return isinstance(user, User) and user.groups.filter(name=Constants.VENDOR_GROUP).exists()

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


def update_sold_product(seller):
    if not isinstance(seller, User) or not is_vendor(seller):
        return False

    order_queryset = Order.objects.filter(is_paid=True, vendor_balance_updated=False)
    if not order_queryset.exists():
        return False
    order_items_queryset = OrderItem.objects.filter(product__product__sold_by=seller, order__in=order_queryset)
    balance_aggregate = order_items_queryset.aggregate(balance=Sum('total_price', output_field=FloatField()))
    balance = balance_aggregate.get('balance', 0.0)
    Balance.objects.filter(user=seller).update(balance=F('balance') + balance)
    Order.objects.filter(order_items__in=order_items_queryset).update(vendor_balance_updated=True)
    batch_size = 100
    objs = [SoldProduct(seller=seller, customer=item.order.user, product=item.product) for item in order_items_queryset]
    while True:
        batch = list(islice(objs, batch_size))
        if not batch:
            break
        SoldProduct.objects.bulk_create(batch, batch_size)
    return True


def get_pending_payment(user):
    pass
