from inventory.models import Visitor, UniqueIP, FacebookLinkHit
from django.db.models import F
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)
X_FORWARDED_FOR_HEADER = "X-Forwarded-For"
FACEBOOK_REQUEST_QUERY = "fbclid"
REMOTE_ADDR = "REMOTE_ADDR"
IP_SEP = ','

class VisitorCounter:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        v, created = Visitor.objects.get_or_create(url=request.path)
        Visitor.objects.filter(pk=v.pk).update(hits=F('hits') + 1)
        response = self.get_response(request)
        return response

class FacebookHitCounter:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if X_FORWARDED_FOR_HEADER in request.META:
            client_ip = request.META.get(X_FORWARDED_FOR_HEADER).split(IP_SEP)[0]
        else:
            client_ip = request.META.get(REMOTE_ADDR)
        if request.method == 'GET' and FACEBOOK_REQUEST_QUERY in request.GET.copy():
            fbclid = request.GET.copy().get(FACEBOOK_REQUEST_QUERY)
            fblh, created = FacebookLinkHit.objects.get_or_create(fbclid=fbclid, ip_address=client_ip)
            FacebookLinkHit.objects.filter(pk=fblh.pk).update(hits=F('hits') + 1)
        response = self.get_response(request)
        return response


class UniqueIPCounter:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        
        if X_FORWARDED_FOR_HEADER in request.META:
            client_ip = request.META.get(X_FORWARDED_FOR_HEADER).split(IP_SEP)[0]
        else:
            client_ip = request.META.get(REMOTE_ADDR)
        logger.info(f"request client ip : {client_ip}")
        logger.info(f"request path : {request.path}")
        v, created = UniqueIP.objects.get_or_create(ip_address=client_ip)
        UniqueIP.objects.filter(pk=v.pk).update(hits=F('hits') + 1)
        response = self.get_response(request)
        return response