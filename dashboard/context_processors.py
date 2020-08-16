from lyshop import settings
from django.contrib.auth.models import User


def dashboard_context(request):
    banner = False
    if request.user.is_authenticated and settings.DASHBOARD_ROOT_PATH in request.path:
        banner = True
    context = {
        'banner' : banner
    }
    return context