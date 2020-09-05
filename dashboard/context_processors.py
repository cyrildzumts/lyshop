from lyshop import settings
from django.contrib.auth.models import User


def dashboard_context(request):
    paths = [settings.ACCOUNT_ROOT_PATH , settings.HOME_URL, settings.DASHBOARD_ROOT_PATH, settings.VENDOR_ROOT_PATH, settings.PAYMENT_ROOT_PATH ]
    banner = len(list(filter(lambda path: path in request.path, paths))) > 0
    context = {
        'banner' : banner
    }
    return context