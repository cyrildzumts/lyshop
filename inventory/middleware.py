from inventory.models import Visitor, UniqueIP
from django.db.models import F
import logging

logger = logging.getLogger(__name__)

class VisitorCounter:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.info("VisitorCounter started...")
        Visitor.objects.update_or_create(defaults={'hits' : F('hits')+1},url=request.path)
        response = self.get_response(request)
        logger.info("VisitorCounter finished...")
        return response


class UniqueIPCounter:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.info("UniquevisitorCounter started...")
        UniqueIP.objects.update_or_create(defaults={'hits' : F('hits')+1}, ip_address=request.META.REMOTE_ADDR)
        response = self.get_response(request)
        logger.info("UniquevisitorCounter finished...")
        return response