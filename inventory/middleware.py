from inventory.models import Visitor, UniqueIP
from django.db.models import F
import logging

logger = logging.getLogger(__name__)

class VisitorCounter:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.info("VisitorCounter started...")
        v, created = Visitor.objects.get_or_create(url=request.path)
        Visitor.objects.filter(pk=v.pk).update(hits=F('hits') + 1)
        response = self.get_response(request)
        logger.info("VisitorCounter finished...")
        return response


class UniqueIPCounter:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.info("UniquevisitorCounter started...")
        v, created = UniqueIP.objects.get_or_create(ip_address=request.META.['REMOTE_ADDR'])
        UniqueIP.objects.filter(pk=v.pk).update(hits=F('hits') + 1)
        response = self.get_response(request)
        logger.info("UniquevisitorCounter finished...")
        return response