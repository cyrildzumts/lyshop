from django.db.models import F, Q, Sum, Count
from catalog.models import ProductVariant, Product
from orders.models import Order
from inventory.models import Visitor, UniqueIP, FacebookLinkHit, SuspiciousRequest
from dashboard.models import LoginReport
from django.contrib.auth.models import User
from django.utils import timezone
from lyshop import utils

import logging

logger = logging.getLogger(__name__)

YEAR_MONTHS_COUNT = 12

def get_orders(year=timezone.now().year, month=timezone.now().month):
    qs_orders = Order.objects.filter(created_at__year=year, created_at__month=month)
    return qs_orders


def report_orders_for_month(year=timezone.now().year, month=timezone.now().month):
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


def report_orders(year=timezone.now().year):
    if year < 0 or year > timezone.now().year :
        error_str = f"report_orders_for_year : invalid year \"{year}\". Only years between 1 and {timezone.now().year} accepted"
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
    
    total_orders = Order.objects.count()

    report = {
        'label': 'Order',
        'year' : year,
        'months': months,
        'data' : data,
        'total_count': total_orders
    }
    return report


def report_orders_price(year=timezone.now().year):
    if year < 0 or year > timezone.now().year :
        error_str = f"report_orders_for_year : invalid year \"{year}\". Only years between 1 and {timezone.now().year} accepted"
        logger.error(error_str)
        raise ValueError(error_str)
    
    data = []
    if year == timezone.now().year:
        MONTH_LIMIT = timezone.now().month
    else :
        MONTH_LIMIT = YEAR_MONTHS_COUNT
    
    months = list(range(1, MONTH_LIMIT + 1))

    for m in months:
        amount = Order.objects.filter(created_at__year=year, created_at__month=m).aggregate(amount=Sum('amount')).get('amount', 0)
        data.append(amount or 0)

    report = {
        'label': 'Order Price',
        'year' : year,
        'months': months,
        'data' : data
    }
    return report



def report_products(year=timezone.now().year):
    if year < 0 or year > timezone.now().year :
        error_str = f"report_products : invalid year \"{year}\". Only years between 1 and {timezone.now().year} accepted"
        logger.error(error_str)
        raise ValueError(error_str)
    
    data = []
    if year == timezone.now().year:
        MONTH_LIMIT = timezone.now().month
    else :
        MONTH_LIMIT = YEAR_MONTHS_COUNT
    
    months = list(range(1, MONTH_LIMIT + 1))

    for m in months:
        count = Product.objects.filter(created_at__year=year, created_at__month=m).aggregate(count=Sum('quantity')).get('count', 0)
        data.append(count or 0)

    total_products = Product.objects.aggregate(count=Sum('quantity')).get('count', 0)
    report = {
        'label': 'Products',
        'year' : year,
        'months': months,
        'data' : data,
        'total_count' : total_products
    }
    return report



def report_for_year(year=timezone.now().year, appName=None, modelName=None, label=None):
    if year < 0 or year > timezone.now().year :
        error_str = f"report_products_for_year : invalid year \"{year}\". Only years between 1 and {timezone.now().year} accepted"
        logger.error(error_str)
        raise ValueError(error_str)

    if isinstance(appName, str) and len(appName) > 0:
        error_str = f"report_for_year : invalid model \"{appName}\". appName value(non empty string) expected"
        logger.error(error_str)
        raise ValueError(error_str)
    
    if isinstance(modelName, str) and len(modelName) > 0:
        error_str = f"report_for_year : invalid model \"{modelName}\". modelName value(non empty string) expected"
        logger.error(error_str)
        raise ValueError(error_str)

    if isinstance(label, str) and len(label) > 0:
        error_str = f"report_for_year : invalid label \"{label}\". label value( non empty string) expected"
        logger.error(error_str)
        raise ValueError(error_str)

    data = []
    if year == timezone.now().year:
        MONTH_LIMIT = timezone.now().month
    else :
        MONTH_LIMIT = YEAR_MONTHS_COUNT
    
    months = list(range(1, MONTH_LIMIT + 1))
    model = None
    try:
        model = utils.get_model(app_name=appName, modelName=modelName)
    except Exception as e:
        error_str = f"report_for_year :  Error on getting model wih modelName \"{modelName}\" in app \"{appName}\""
        logger.error(error_str)
        raise e

    for m in months:
        data.append(model.objects.filter(created_at__year=year, created_at__month=m).count())

    report = {
        'label': label,
        'year' : year,
        'months': months,
        'data' : data
    }
    return report



def report_new_users(year=timezone.now().year):
    if year < 0 or year > timezone.now().year :
        error_str = f"report_new_users : invalid year \"{year}\". Only years between 1 and {timezone.now().year} accepted"
        logger.error(error_str)
        raise ValueError(error_str)
    
    data = []
    if year == timezone.now().year:
        MONTH_LIMIT = timezone.now().month
    else :
        MONTH_LIMIT = YEAR_MONTHS_COUNT
    
    months = list(range(1, MONTH_LIMIT + 1))

    for m in months:
        data.append(User.objects.filter(date_joined__year=year, date_joined__month=m).count())
    
    total_users = User.objects.count()

    report = {
        'label': 'New Users',
        'year' : year,
        'months': months,
        'data' : data,
        'total_count' : total_users
    }
    return report


def report_online_users():
    pass


def report_log_users(year=timezone.now().year):
    if year < 0 or year > timezone.now().year :
        error_str = f"report_new_users : invalid year \"{year}\". Only years between 1 and {timezone.now().year} accepted"
        logger.error(error_str)
        raise ValueError(error_str)
    
    data = []
    if year == timezone.now().year:
        MONTH_LIMIT = timezone.now().month
    else :
        MONTH_LIMIT = YEAR_MONTHS_COUNT
    
    months = list(range(1, MONTH_LIMIT + 1))

    for m in months:
        data.append(LoginReport.objects.filter(date_login__year=year, date_login__month=m).count())

    report = {
        'label': 'Users Log',
        'year' : year,
        'months': months,
        'data' : data
    }
    return report


def report_visitors(year=timezone.now().year):
    if year < 0 or year > timezone.now().year :
        error_str = f"report_visitors : invalid year \"{year}\". Only years between 1 and {timezone.now().year} accepted"
        logger.error(error_str)
        raise ValueError(error_str)
    
    data = []
    Models = [Visitor, FacebookLinkHit, SuspiciousRequest]
    if year == timezone.now().year:
        MONTH_LIMIT = timezone.now().month
    else :
        MONTH_LIMIT = YEAR_MONTHS_COUNT
    
    months = list(range(1, MONTH_LIMIT + 1))
    for model in Models:
        model_data = []
        for m in months:
            hits = model.objects.filter(created_at__year=year, created_at__month=m).aggregate(hits=Sum('hits')).get('hits')
            model_data.append(hits or 0)
        data.append(model_data)

    model_data = []
    for m in months:
        hits = UniqueIP.objects.filter(created_at__year=year, created_at__month=m).count()
        model_data.append(hits)
    
    data.append(model_data)

    total_unique_visitors = UniqueIP.objects.count()
    total_visitors = Visitor.objects.aggregate(hits=Sum('hits')).get('hits')
    total_facebook_visitors = FacebookLinkHit.objects.aggregate(hits=Sum('hits')).get('hits')
    total_suspicious_visitors = SuspiciousRequest.objects.aggregate(hits=Sum('hits')).get('hits')

    report = {
        'labels': ['Visitors', 'Facebook Visitors', 'Unique Visitors'],
        'year' : year,
        'months': months,
        'data' : data,
        'total_unique_visitors' : total_unique_visitors,
        'total_visitors' : total_visitors,
        'total_facebook_visitors' : total_facebook_visitors,
        'total_suspicious_visitors': total_suspicious_visitors

    }
    return report

