from lyshop import settings
from django.contrib.auth.models import User
from cart import cart_service
from orders import orders_service
from shipment import shipment_service
import logging

logger = logging.getLogger(__name__)

def site_context(request):
    is_dashboard_allowed = False
    cart_items_count = 0
    if request.user.is_authenticated:
        
        is_dashboard_allowed = request.user.has_perm('dashboard.can_view_dashboard')
        cart_items_count = cart_service.cart_items_count(request.user)
    context = {
        'site_name' : settings.SITE_NAME,
        'SITE_NAME' : settings.SITE_NAME,
        'SITE_HOST' : settings.SITE_HOST,
        'META_KEYWORDS': settings.META_KEYWORDS,
        'META_DESCRIPTION': settings.META_DESCRIPTION,
        'redirect_to' : '/',
        'is_dashboard_allowed' : is_dashboard_allowed,
        'dev_mode' : settings.DEV_MODE,
        'ALLOW_GOOGLE_ANALYTICS' : settings.ALLOW_GOOGLE_ANALYTICS,
        'cart_items_count': cart_items_count,
        'CURRENCY' : settings.CURRENCY,
        'next_url' : request.path,
        'ship_modes' : shipment_service.get_ship_modes(),
        'payment_methods' : orders_service.get_payment_methods(),
    }
    return context