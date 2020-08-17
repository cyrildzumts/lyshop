from lyshop import settings
from django.contrib.auth.models import User


def dashboard_context(request):
    context = {
        'banner' : settings.HOME_URL == request.path or settings.DASHBOARD_ROOT_PATH in request.path or settings.ACCOUNT_ROOT_PATH in request.path
    }
    return context