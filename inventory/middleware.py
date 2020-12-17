from inventory.models import Visitor, UniqueIP
from django.db.models import F
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class VisitorCounter:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.info(f"VisitorCounter started... for path {request.path}")
        v, created = Visitor.objects.get_or_create(url=request.path)
        Visitor.objects.filter(pk=v.pk).update(hits=F('hits') + 1)
        response = self.get_response(request)
        logger.info(f"VisitorCounter finished...for path {request.path}")
        return response


class UniqueIPCounter:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.info(f"UniquevisitorCounter started...for ip address {request.META['REMOTE_ADDR']}")
        logger.info(f"UniquevisitorCounter started-  X-Forwarded-For address {request.META.get('X-Forwarded-For')}")
        logger.info(f"UniquevisitorCounter started - headers {request.headers}")
        v, created = UniqueIP.objects.get_or_create(ip_address=request.META['REMOTE_ADDR'])
        UniqueIP.objects.filter(pk=v.pk).update(hits=F('hits') + 1)
        response = self.get_response(request)
        return response