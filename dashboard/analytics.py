from django.db.models import F, Q, Sum, Count, Max, Min, Avg
from catalog.models import ProductVariant, Product
from orders.models import Order
from inventory.models import Visitor, UniqueIP, FacebookLinkHit, SuspiciousRequest, GoogleAdsHit
from inventory import constants as Inventory_Constants
from dashboard.models import LoginReport
from dashboard import Constants
from django.contrib.auth.models import User
from django.utils import timezone
from lyshop import utils
from operator import or_
from functools import reduce
from itertools import islice
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
        data.append({'x': f"{year}-{m:02}", 'y' : Order.objects.filter(created_at__year=year, created_at__month=m).count()})
    
    total_orders = Order.objects.count()

    report = {
        'label': f"Orders {year}",
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
        amount = Order.objects.filter(created_at__year=year, created_at__month=m).aggregate(amount=Sum('amount')).get('amount') or 0
        data.append({'x': f"{year}-{m:02}", 'y' : amount})

    report = {
        'label': f"Orders Prices {year}",
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
    product_type_report = Product.objects.filter(quantity__gt=0).values(type_name=F('product_type__display_name')).annotate(count=Count('product_type')).order_by()
    product_gender_report = Product.objects.filter(quantity__gt=0).values('gender').annotate(count=Count('gender')).order_by()
    product_brand_report = Product.objects.filter(quantity__gt=0).values(brand_name=F('brand__display_name')).annotate(count=Count('brand')).order_by()
    product_price_reports = Product.objects.filter(quantity__gt=0).aggregate(total_price=Sum('price'), min_price=Min('price'), max_price=Max('price'), avg_price=Avg('price'))

    if year == timezone.now().year:
        MONTH_LIMIT = timezone.now().month
    else :
        MONTH_LIMIT = YEAR_MONTHS_COUNT
    
    months = list(range(1, MONTH_LIMIT + 1))

    for m in months:
        
        count = Product.objects.filter(created_at__year=year, created_at__month=m).aggregate(count=Sum('quantity')).get('count') or 0
        data.append({'x': f"{year}-{m:02}", 'y' : count})

    total_products = Product.objects.aggregate(count=Sum('quantity')).get('count', 0)
    report = {
        'label': f"Products {year}",
        'year' : year,
        'months': months,
        'data' : data,
        'total_count' : total_products,
        'detail_reports' : {
            'product_type_report': product_type_report,
            'product_gender_report': product_gender_report,
            'product_brand_report': product_brand_report,
            'product_price_reports': product_price_reports
        }
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
        data.append( {'x': f"{year}-{m:02}", 'y' : User.objects.filter(date_joined__year=year, date_joined__month=m).count()})
    
    total_users = User.objects.count()

    report = {
        'label': f"New Users {year}",
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
        data.append({'x': f"{year}-{m:02}", 'y' : LoginReport.objects.filter(date_login__year=year, date_login__month=m).count()})

    report = {
        'label': f"Log users {year}",
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
    Models = [Visitor, FacebookLinkHit, SuspiciousRequest, GoogleAdsHit]
    if year == timezone.now().year:
        MONTH_LIMIT = timezone.now().month
    else :
        MONTH_LIMIT = YEAR_MONTHS_COUNT
    
    months = list(range(1, MONTH_LIMIT + 1))
    for model in Models:
        data_model = []
        for m in months:
            hits = model.objects.filter(created_at__year=year, created_at__month=m).aggregate(hits=Sum('hits')).get('hits') or 0
            data_model.append({'x' : f"{year}-{m:02}", 'y': hits})
        data.append(data_model)

    data_model = []
    for m in months:
        hits = UniqueIP.objects.filter(created_at__year=year, created_at__month=m).count()
        data_model.append({'x' : f"{year}-{m:02}", 'y': hits})
    data.append(data_model)

    total_unique_visitors = UniqueIP.objects.count()
    total_visitors = Visitor.objects.aggregate(hits=Sum('hits')).get('hits') or 0
    total_facebook_visitors = FacebookLinkHit.objects.aggregate(hits=Sum('hits')).get('hits') or 0
    total_google_visitors = GoogleAdsHit.objects.aggregate(hits=Sum('hits')).get('hits') or 0
    total_suspicious_visitors = SuspiciousRequest.objects.aggregate(hits=Sum('hits')).get('hits') or 0
    report = {
        'labels': [f"Vistors {year}", f"Facebook Vistors {year}", f"Suspicious Vistors {year}",f"Google Vistors {year}", f"Unique Vistors {year}"],
        #'labels': [f"Vistors", f"Facebook Vistors", f"Suspicious Vistors", f"Google Vistors", f"Unique Vistors"],
        'year' : year,
        'months': months,
        'data' : data,
        'total_unique_visitors' : total_unique_visitors,
        'total_visitors' : total_visitors,
        'total_facebook_visitors' : total_facebook_visitors,
        'total_google_visitors' : total_google_visitors,
        'total_suspicious_visitors': total_suspicious_visitors
    }
    return report


def refresh_suspicious_request():

    queryset = Visitor.objects.exclude(reduce(or_, (Q(url__icontains=p) for p in Inventory_Constants.VALID_PATHS))).values('url', 'hits')
    ip_address = '0.0.0.0'
    batch_size = 100
    if not queryset.exists():
        logger.warning("No Suspicious requests find from old visitors")
        return False
    
    objs = (SuspiciousRequest(url=entry['url'], hits=entry['hits'], ip_address=ip_address) for entry in queryset)
    while True:
        batch = list(islice(objs, batch_size))
        if not batch:
            break
        SuspiciousRequest.objects.bulk_create(batch, batch_size)
    return True



def customers_report():
    return User.objects.annotate(spent=Sum('orders__total'), last_ordered=Max('orders__created_at'))


def sellers_report():
    return User.objects.filter(groups__name=Constants.SELLER_GROUP).annotate(
        sales=Sum('vendor_sold_products__total_price'), product_count=Sum('vendor_sold_products__product__product__quantity'),
        total_views=Sum('vendor_sold_products__product__product__view_count'),
        last_sold=Max('vendor_sold_products__created_at'), total_sold=Sum('vendor_sold_products__quantity')).order_by()