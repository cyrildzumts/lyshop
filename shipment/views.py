from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied, SuspiciousOperation

from django.contrib.auth.models import User, Group, Permission
from django.http import Http404
from django.http import HttpResponseRedirect
from django.http import HttpResponseBadRequest
from django.http import HttpResponse
from django.urls import reverse, resolve
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseForbidden
from django.contrib import messages
from django.db.models import F, Q, Count, Sum
from django.utils import timezone
from shipment.models import Shipment, ShippedItem, ShipmentStatusHistory
from shipment.forms import ShipmentForm
from lyshop import utils
import logging

logger = logging.getLogger(__name__)

# Create your views here.


@login_required
def shipment_home(request):
    queryset = Shipment.objects.all()[:5]
    context = {
        'page_title' : _('Shipments'),
        'recent_shipments' : queryset
    }
    temlate_name = 'shipment/shipment_home.html'
    return render(request, template_name, context)


@login_required
def shipments(request):
    queryset = Shipment.objects.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, utils.PAGINATED_BY)
    try:
        list_set = paginator.page(page)
    except PageNotAnInteger:
        list_set = paginator.page(1)
    except EmptyPage:
        list_set = None
    context = {
        'page_title' : _('Shipments'),
        'shipment_list' : list_set
    }
    temlate_name = 'shipment/shipment_list.html'

    return render(request, template_name, context)


@login_required
def shipment_detail(request, shipment_uuid):
    shipment = get_object_or_404(Shipment, shipment_uuid=shipment_uuid)

    context = {
        'page_title' : _('Shipment'),
        'shipment' : shipment
    }
    template_name = 'shipment/shipment_detail.html'
    return render(request, template_name, context)


@login_required
def shipment_update(request, shipment_uuid):
    shipment = get_object_or_404(Shipment, shipment_uuid=shipment_uuid)

    if request.method == 'POST':
        postdata = utils.get_postdata(request)
        form = ShipmentForm(instance=shipment, postdata)
        if form.is_valid():
            shipment = form.save()
            messages.success(request, _('Shipment updated'))
            logger.info(f"Shipment {shipement.id} updated")
            return redirect(shipment)

    form = ShipmentForm(instance = shipment)
    context = {
        'page_title' : _('Shipment Update'),
        'shipment' : shipment,
        'form' : form
    }
    template_name = 'shipment/shipment_update.html'
    return render(request, template_name, context)


@login_required
def shippeditem_detail(request, shippeditem_uuid):
    pass


@login_required
def shipment_history(request, shipment_uuid):
    shipment = get_object_or_404(Shipment, shipment_uuid=shipment_uuid)
    queryset = ShipmentStatusHistory.objects.filter(shipment__shipment_uuid=shipment_uuid)
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, utils.PAGINATED_BY)
    try:
        list_set = paginator.page(page)
    except PageNotAnInteger:
        list_set = paginator.page(1)
    except EmptyPage:
        list_set = None
    context = {
        'page_title' : _('Shipment Histories'),
        'history_list':  list_set,
        'shipment' : shipment
    }
    template_name = 'shipment/shipment_histories.html'
    return render(request, template_name, context)


@login_required
def shipment_history_detail(request, history_uuid):
    history = get_object_or_404(ShipmentStatusHistory, history_uuid=history_uuid)
    context = {
        'page_title' : _('Shipment History'),
        'history':  history
    }
    template_name = 'shipment/shipment_history.html'
    return render(request, template_name, context)