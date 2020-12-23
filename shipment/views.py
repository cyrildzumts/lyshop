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
from dashboard.permissions import PermissionManager
from shipment.models import Shipment, ShippedItem, ShipmentStatusHistory, ShipMode
from shipment import shipment_service, constants as Constants
from shipment.forms import ShipmentForm, ShipModeForm
from lyshop import utils, conf as GLOBAL_CONF
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
    template_name = 'shipment/shipment_home.html'
    return render(request, template_name, context)


@login_required
def shipments(request):
    queryset = Shipment.objects.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, GLOBAL_CONF.PAGINATED_BY)
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
    template_name = 'shipment/shipment_list.html'

    return render(request, template_name, context)


@login_required
def order_ready_for_shipment(request):
    queryset = shipment_service.get_orders_ready_for_shipment()
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, GLOBAL_CONF.PAGINATED_BY)
    try:
        list_set = paginator.page(page)
    except PageNotAnInteger:
        list_set = paginator.page(1)
    except EmptyPage:
        list_set = None
    context = {
        'page_title' : _('Shipment Waiting'),
        'order_list' : list_set
    }
    template_name = 'shipment/order_ready_list.html'

    return render(request, template_name, context)


@login_required
def shipment_detail(request, shipment_uuid):
    shipment = get_object_or_404(Shipment.objects.select_related('order__address'), shipment_uuid=shipment_uuid)

    context = {
        'page_title' : _('Shipment'),
        'shipment' : shipment
    }
    template_name = 'shipment/shipment_detail.html'
    return render(request, template_name, context)


@login_required
def shipment_delete(request, shipment_uuid):
    Shipment.objects.filter(shipment_uuid=shipment_uuid).delete()
    logger.info(f"Shipment {shipment_uuid} delete by user {request.user}")
    return redirect('shipment:shipments')


@login_required
def shipment_update(request, shipment_uuid):
    shipment = get_object_or_404(Shipment, shipment_uuid=shipment_uuid)

    if request.method == 'POST':
        postdata = utils.get_postdata(request)
        form = ShipmentForm(postdata, instance=shipment)
        if form.is_valid():
            shipment = form.save()
            shipment_service.update_order_status(shipment.order, shipment, request.user)
            ShipmentStatusHistory.objects.create(shipment_status=shipment.shipment_status, shipment_ref_id=shipment.id,shipment=shipment, changed_by=shipment.last_changed_by)
            messages.success(request, _('Shipment updated'))
            logger.info(f"Shipment {shipment.id} updated")
            return redirect(shipment)
        else:
            messages.error(request, _('Shipment Invalid'))
            logger.error(f"Shipment Form not valid.")
            logger.error(form.error.items())

    form = ShipmentForm(instance=shipment)
    context = {
        'page_title' : _('Shipment Update'),
        'shipment' : shipment,
        'SHIPMENT_STATUS': Constants.SHIPMENT_STATUS,
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




@login_required
def ship_mode_create(request):
    template_name = 'shipment/ship_mode_create.html'
    page_title = _('New Payment Method')
    username = request.user.username

    if not PermissionManager.user_can_add_shipment(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    context = {
        'page_title': page_title,
        'SHIP_MODE' : Constants.SHIP_MODE
    }
    if request.method == 'POST':
        postdata = utils.get_postdata(request)
        ship_mode, created = shipment_service.create_ship_mode(postdata)
        if created:
            messages.success(request,_('New Ship Mode created'))
            logger.info(f'[ OK ] New Ship Mode {ship_mode} added by user {request.user.username}' )
            return redirect('shipment:ship_modes')
        else:
            messages.error(request,_('Ship Mode not created'))
            logger.error(f'[ NOT OK ] Error on adding New Ship Mode by user {request.user.username}.' )

    form = ShipModeForm()
    context['form'] = form
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)
    



@login_required
def ship_modes(request):
    template_name = 'shipment/ship_mode_list.html'
    page_title = _('Ship Mode List')
    
    username = request.user.username

    if not PermissionManager.user_can_view_shipment(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    context = {
        'page_title': page_title,
    }
    queryset = shipment_service.get_ship_modes()
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, GLOBAL_CONF.PAGINATED_BY)
    try:
        list_set = paginator.page(page)
    except PageNotAnInteger:
        list_set = paginator.page(1)
    except EmptyPage:
        list_set = None
    context['ship_mode_list'] = list_set
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)

@login_required
def ship_mode_detail(request, ship_uuid=None):
    template_name = 'shipment/ship_mode_detail.html'
    page_title = _('Ship Mode')
    username = request.user.username

    if not PermissionManager.user_can_view_shipment(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    context = {
        'page_title': page_title
    }

    ship_mode = get_object_or_404(ShipMode, ship_uuid=ship_uuid)
    context['ship_mode'] = ship_mode
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)

@login_required
def ship_mode_update(request, ship_uuid):
    template_name = 'shipment/ship_mode_update.html'
    page_title = _('Edit Ship Mode')
    username = request.user.username

    if not PermissionManager.user_can_change_shipment(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    ship_mode = get_object_or_404(ShipMode, ship_uuid=ship_uuid)
    if request.method == 'POST':
        postdata = utils.get_postdata(request)
        ship_mode, updated = shipment_service.update_ship_mode(postdata, ship_mode)
        if updated :
            messages.success(request,_('Ship Mode updated'))
            logger.info(f'[ OK ] Ship Mode \"{ship_mode}\" updated by user {request.user.username}' )
            return redirect(ship_mode.get_absolute_url())
        else:
            messages.error(request,_('Error when updating Ship Mode'))
            logger.error(f'[ NOT OK ] Error on updating Ship Mode \"{ship_mode}\" added by user {request.user.username}' )

    form = ShipModeForm(instance=ship_mode)
    context = {
        'page_title': page_title,
        'form' : form,
        'ship_mode': ship_mode,
        'SHIP_MODE' : Constants.SHIP_MODE
    }
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)


@login_required
def ship_mode_delete(request, ship_uuid):
    username = request.user.username
    if not PermissionManager.user_can_delete_shipment(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    if request.method != "POST":
        raise SuspiciousOperation('Bad request. POST request expected but received a GET request')
    ship_mode = get_object_or_404(ShipMode, ship_uuid=ship_uuid)
    PaymentMethod.objects.filter(pk=ship_mode.pk).delete()
    return redirect('shipment:ship-modes')


@login_required
def ship_modes_delete(request):
    username = request.user.username

    if not PermissionManager.user_can_delete_shipment(request.user):
        logger.warning(f"PermissionDenied to user \"{username}\" for path \"{request.path}\"")
        raise PermissionDenied
    if request.method != "POST":
        raise SuspiciousOperation('Bad request')
    postdata = utils.get_postdata(request)
    id_list = postdata.getlist('ship_modes')

    if len(id_list):
        mode_list = list(map(int, id_list))
        ShipMode.objects.filter(id__in=mode_list).delete()
        messages.success(request, f"Ship Mode \"{mode_list}\" deleted")
        logger.info(f"Ship Mode \"{method_list}\" deleted by user {username}")
        
    else:
        messages.error(request, f"Ship Mode  could not be deleted")
        logger.error(f"ID list invalid. Error : {id_list}")
    return redirect('shipment:ship_modes')