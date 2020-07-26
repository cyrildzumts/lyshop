from django.db.models import F, Q, Sum, Count
from catalog.models import ProductVariant, Product
from orders.models import Order
from django.contrib.auth.models import User
from django.utils import timezone

import logging

logger = logging.getLogger(__name__)

YEAR_MONTHS_COUNT = 12

def get_orders(year=timezone.now().year, month=timezone.now().month):
    logger.info(f"Analytics get_orders() for date year=\"{year}\" - month=\"{month}\" ")
    qs_orders = Order.objects.filter(created_at__year=year, created_at__month=month)
    return qs_orders


def report_orders(year=timezone.now().year, month=timezone.now().month):
    logger.info(f"Report Orders for date year=\"{year}\" - month=\"{month}\"")
    if year < 0 or year > timezone.now().year :
        error_str = f"report_orders : invalid year \"{year}\". Only years between 1 and {timezone.now().year} accepted"
        logger.error(error_str)
        raise ValueError(error_str)
    if month < 0 or month > 12:
        error_str = f"report_orders : invalid month \"{month}\". Only months between 1 and 12 accepted"
        logger.error(error_str)
        raise ValueError(error_str)

    count = Order.objects.filter(created_at__year=year, created_at__month=month).count()
    
    report = {
        'label': 'Order',
        'year' : year,
        'months': [month],
        'data' : [count]
    }
    return report


def report_orders_for_year(year=timezone.now().year):
    logger.info(f"Report Orders for date year=\"{year}\"")
    if year < 0 or year > timezone.now().year :
        error_str = f"report_orders : invalid year \"{year}\". Only years between 1 and {timezone.now().year} accepted"
        logger.error(error_str)
        raise ValueError(error_str)
    
    data = []
    if year == timezone.now().year:
        MONTH_LIMIT = timezone.now().month
    else :
        MONTH_LIMIT = YEAR_MONTHS_COUNT
    
    months = list(range(1, MONTH_LIMIT + 1))

    for m in months:
        data.append(Order.objects.filter(created_at__year=year, created_at__month=m).count())

    report = {
        'label': 'Order',
        'year' : year,
        'months': months,
        'data' : data
    }
    return report