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
        
        if "X-Forwarded-For" in request.META:
            client_ip = request.META.get('X-Forwarded-For').split()[0]
        else:
            client_ip = request.META.get('REMOTE_ADDR')
        logger.info(f"UniquevisitorCounter started...for ip address {client_ip}")
        v, created = UniqueIP.objects.get_or_create(ip_address=client_ip)
        UniqueIP.objects.filter(pk=v.pk).update(hits=F('hits') + 1)
        response = self.get_response(request)
        return response