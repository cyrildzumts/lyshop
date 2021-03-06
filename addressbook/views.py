from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.contrib.auth.models import User
from addressbook import constants as Addressbook_Constants, addressbook_service
from addressbook.models import Address
from addressbook.forms import AddressForm
from lyshop import settings, utils, conf as GLOBAL_CONF
import json
import logging
import uuid

logger = logging.getLogger(__name__)

# Create your views here.


@login_required
def addressbook(request):
    template_name = "addressbook/addressbook.html"
    username = request.user.username
    context = {}
    queryset = Address.objects.filter(user=request.user).order_by('-created_at')
    page_title = _("Addressbook") + " - " + settings.SITE_NAME
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, GLOBAL_CONF.PAGINATED_BY)
    try:
        list_set = paginator.page(page)
    except PageNotAnInteger:
        list_set = paginator.page(1)
    except EmptyPage:
        list_set = None
    context['page_title'] = page_title
    context['address_list'] = list_set
    return render(request,template_name, context)

@login_required
def addresses(request):
    template_name = "addressbook/address_list.html"
    username = request.user.username
    context = {}
    queryset = Address.objects.filter(user=request.user).order_by('-created_at')
    page_title = _("Addresses") + " - " + settings.SITE_NAME
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, GLOBAL_CONF.PAGINATED_BY)
    try:
        list_set = paginator.page(page)
    except PageNotAnInteger:
        list_set = paginator.page(1)
    except EmptyPage:
        list_set = None
    context['page_title'] = page_title
    context['address_list'] = list_set
    return render(request,template_name, context)



@login_required
def address_detail(request, address_uuid=None):
    template_name = 'addressbook/address_detail.html'
    username = request.user.username
    page_title = _('Address')

    address = get_object_or_404(Address,user=request.user, address_uuid=address_uuid)
    context = {
        'page_title': page_title,
        'address': address,
    }
    return render(request,template_name, context)


@login_required
def address_update(request, address_uuid=None):
    username = request.user.username
    template_name = 'addressbook/address_update.html'
    page_title = _('Address Update')
    context = {
        'page_title': page_title,
    }
    form = None
    obj = get_object_or_404(Address, address_uuid=address_uuid, user=request.user)
    username = request.user.username
    if request.method == 'POST':
        postdata = utils.get_postdata(request)
        updated_address = addressbook_service.update_address(obj, postdata)
        if updated_address:
            messages.success(request, _('Address updated'))
            logger.info(f'address {updated_address} updated by user \"{username}\"')
            return redirect('addressbook:address-detail', address_uuid=address_uuid)
        else:
            messages.error(request, _('Address not updated'))
            logger.error(f'Error on updating address. Action requested by user \"{username}\"')

    form = AddressForm(instance=obj)
    context['form'] = form
    context['address'] = obj
    context['ADDRESS_TYPES'] = Addressbook_Constants.ADDRESS_TYPES
    return render(request, template_name, context)

@login_required
def address_delete(request, address_uuid=None):
    username = request.user.username
    obj = get_object_or_404(Address, address_uuid=address_uuid, user=request.user)
    Address.objects.filter(pk=obj.pk).delete()
    logger.info(f'Address \"{obj}\" deleted by user \"{request.user.username}\"')
    messages.success(request, _('Address deleted'))
    return redirect('addressbook:addressbook')

@login_required
def address_toggle_favorite(request, address_uuid=None):
    username = request.user.username
    obj = get_object_or_404(Address, address_uuid=address_uuid, user=request.user)
    toggled = addressbook_service.toggle_favorite(obj)
    logger.info(f'Address \"{obj}\" favorite changed by user \"{request.user.username}\"')
    messages.success(request, _('Address changed'))
    return redirect('addressbook:addressbook')


@login_required
def addresses_delete(request):
    username = request.user.username
    
    postdata = utils.get_postdata(request)
    id_list = postdata.getlist('addresses')

    if len(id_list):
        address_id_list = list(map(int, id_list))
        Address.objects.filter(id__in=address_id_list, user=request.user).delete()
        messages.success(request, f"Addresses \"{id_list}\" deleted")
        logger.info(f"Addresses \"{id_list}\" deleted by user {username}")
        
    else:
        messages.error(request, f"Addresses \"{id_list}\" could not be deleted")
        logger.error(f"ID list invalid. Error : {id_list}")
    return redirect('addressbook:addressbook')


@login_required
def address_create(request):
    username = request.user.username
    
    template_name = 'addressbook/address_create.html'
    page_title = _('New Address')
    
    context = {
        'page_title': page_title,
    }
    
    if request.method == 'POST':
        postdata = utils.get_postdata(request)
        address = addressbook_service.create_address(postdata)
        if address:
            messages.success(request, _('New Address created'))
            logger.info(f'New Address {address} added by user \"{username}\"')
            return redirect('addressbook:addressbook')
        else:
            messages.error(request, _('Address not created'))
            logger.error(f'Error on creating new address. Action requested by user \"{username}\"')

    form = AddressForm()
    context['form'] = form
    context['ADDRESS_TYPES'] = Addressbook_Constants.ADDRESS_TYPES
    return render(request, template_name, context)
