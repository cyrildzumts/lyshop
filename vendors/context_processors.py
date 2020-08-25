from lyshop import settings
from django.contrib.auth.models import User
from vendors import vendors_service


def vendor_context(request):
    is_seller = request.user.is_authenticated and vendors_service.is_vendor(user=request.user)
    show_balance = is_seller and settings.VENDOR_ROOT_PATH in request.path
    balance = None
    if show_balance:
        balance = vendors_service.get_vendor_balance(request.user)
    context = {
        'is_seller' : is_seller,
        'balance' : balance
    }
    return context