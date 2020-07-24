from django.db.models import F, Q, Sum, Count
from catalog.models import ProductVariant, Product
from orders.models import Order
from django.contrib.auth.models import User
from django.utils import timezone

import logging

logger = logging.getLogger(__name__)

def get_orders(year=timezone.now().year, month=timezone.now().month):
    logger.info(f"Report Order for date year=\"{year}\" - month=\"{month}\" ")
    qs_orders = Order.objects.filter(created_at__year=year, created_at__month=month)
    return qs_orders
