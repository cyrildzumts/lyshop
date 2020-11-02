from lyshop import settings
from django.contrib.auth.models import User
from vendors import vendors_service


def can_add_balance(path):
    return settings.VENDOR_ROOT_PATH in path or settings.USER_PATH in path or settings.ACCOUNT_ROOT_PATH in path

def vendor_context(request):
    is_seller = vendors_service.is_vendor(user=request.user)
    balance = None
    home_variables = {}
    if is_seller and can_add_balance(request.path):
        balance = vendors_service.get_vendor_balance(request.user)
        home_variables = vendors_service.get_vendor_home_variable(request.user)

    context = {
        'is_seller' : is_seller,
        'balance' : balance
    }
    context.update(home_variables)
    return context