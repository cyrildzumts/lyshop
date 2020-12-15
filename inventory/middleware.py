from inventory.models import Visitor, UniqueIP
from django.db.models import F


class VisitorCounter:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        Visitor.objects.updatete_or_create(defaults={'hits' : F('hits')+1},url=request.path)
        response = self.get_response(request)

        return response


class UniqueIPCounter:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        UniqueIP.objects.update_or_create(defaults={'hits' : F('hits')+1}, ip_address=request.META.REMOTE_ADDR)
        response = self.get_response(request)

        return response