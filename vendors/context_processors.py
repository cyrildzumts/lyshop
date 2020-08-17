from lyshop import settings
from django.contrib.auth.models import User
from vendors import vendors_service


def vendor_context(request):

    context = {
        'is_seller' : request.user.is_authenticated and vendors_service.is_vendor(user=request.user)
    }
    return context