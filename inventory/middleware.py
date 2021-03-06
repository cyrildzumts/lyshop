from inventory.models import Visitor, UniqueIP, FacebookLinkHit, SuspiciousRequest, GoogleAdsHit
from django.db.models import F
from django.utils import timezone
from inventory import constants as Constants
import logging

logger = logging.getLogger(__name__)

def is_excluded_path(path):
    for p in Constants.EXCLUDES_PATHS:
        if p == path or p in path:
            return True
    return False

def is_accepted_path(path):
    for p in Constants.ACCEPTED_PATHS:
        if p == path or (p != '/' and p in path):
            return True
    return False

def is_suspicious_path(path):
    for p in Constants.VALID_PATHS:
        if p == path or (p != '/' and p in path) or path == '/':
            return False
    return True


class OnlineUserTracker:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if  is_accepted_path(request.path) and not is_excluded_path(request.path):
            v, created = Visitor.objects.get_or_create(url=request.path)
            Visitor.objects.filter(pk=v.pk).update(hits=F('hits') + 1)
        response = self.get_response(request)
        return response


class VisitorCounter:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if  is_accepted_path(request.path) and not is_excluded_path(request.path):
            v, created = Visitor.objects.get_or_create(url=request.path)
            Visitor.objects.filter(pk=v.pk).update(hits=F('hits') + 1)
        response = self.get_response(request)
        return response

class FacebookHitCounter:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if is_accepted_path(request.path) and not is_excluded_path(request.path):

            if Constants.X_FORWARDED_FOR_HEADER in request.META:
                client_ip = request.META.get(Constants.X_FORWARDED_FOR_HEADER).split(Constants.IP_SEP)[0]
            else:
                client_ip = request.META.get(Constants.REMOTE_ADDR)
            if request.method == 'GET' and Constants.FACEBOOK_REQUEST_QUERY in request.GET.copy():
                fbclid = request.GET.copy().get(Constants.FACEBOOK_REQUEST_QUERY)
                fblh, created = FacebookLinkHit.objects.get_or_create(fbclid=fbclid, ip_address=client_ip)
                FacebookLinkHit.objects.filter(pk=fblh.pk).update(hits=F('hits') + 1)
        response = self.get_response(request)
        return response


class GoogleADSHitCounter:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if is_accepted_path(request.path) and not is_excluded_path(request.path):

            if Constants.X_FORWARDED_FOR_HEADER in request.META:
                client_ip = request.META.get(Constants.X_FORWARDED_FOR_HEADER).split(Constants.IP_SEP)[0]
            else:
                client_ip = request.META.get(Constants.REMOTE_ADDR)
            if request.method == 'GET' and Constants.GOOGLE_REQUEST_QUERY in request.GET.copy():
                gclid = request.GET.copy().get(Constants.GOOGLE_REQUEST_QUERY)
                gadsh, created = GoogleAdsHit.objects.get_or_create(gclid=gclid, ip_address=client_ip)
                GoogleAdsHit.objects.filter(pk=gadsh.pk).update(hits=F('hits') + 1)
        response = self.get_response(request)
        return response


class UniqueIPCounter:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if is_accepted_path(request.path) and not is_excluded_path(request.path):
            if Constants.X_FORWARDED_FOR_HEADER in request.META:
                client_ip = request.META.get(Constants.X_FORWARDED_FOR_HEADER).split(Constants.IP_SEP)[0]
            else:
                client_ip = request.META.get(Constants.REMOTE_ADDR)
            logger.info(f"request client ip : {client_ip}")
            logger.info(f"request path : {request.path}")
            v, created = UniqueIP.objects.get_or_create(ip_address=client_ip)
            UniqueIP.objects.filter(pk=v.pk).update(hits=F('hits') + 1)
        response = self.get_response(request)
        return response


class SuspiciousRequestCounter:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if is_suspicious_path(request.path):

            if Constants.X_FORWARDED_FOR_HEADER in request.META:
                client_ip = request.META.get(Constants.X_FORWARDED_FOR_HEADER).split(Constants.IP_SEP)[0]
            else:
                client_ip = request.META.get(Constants.REMOTE_ADDR)
            src, created = SuspiciousRequest.objects.get_or_create(url=request.path, ip_address=client_ip)
            SuspiciousRequest.objects.filter(pk=src.pk).update(hits=F('hits') + 1)
            logger.info(f"suspicious request client ip : {client_ip}")
            logger.info(f"suspicious request path : {request.path}")
        response = self.get_response(request)
        return response