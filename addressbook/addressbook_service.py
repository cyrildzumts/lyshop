
from django.contrib.auth.models import User
from django.db.models import F
from django.core.exceptions import ObjectDoesNotExist
from addressbook.models import Address
from addressbook import constants as Addressbook_Constants
from addressbook.forms import AddressModelForm
from core import core_tools
from lyshop import utils, conf
import logging
import uuid

logger = logging.getLogger(__name__)


def get_addresses(user):
    if  not isinstance(user, User):
        return None
    return Address.objects.filter(user=user)


def get_address(address_id):
    address = None
    try:
        if isinstance(address_id, int):
            address = Address.objects.get(pk=address_id)
        elif isinstance(address_id, uuid.uuid4):
            address = Address.objects.get(address_uuid=address_id)
    except ObjectDoesNotExist as e:
        address = None
    return address

def get_address_uuid(address_uuid):
    try:
        address = Address.objects.get(address_uuid=address_uuid)
    except ObjectDoesNotExist as e:
        address = None
    return address

def toggle_address_active(address, requester, state):
    if  not isinstance(requester, User):
        return False
    if  not isinstance(address, Address):
        return False

    if  not isinstance(state, bool):
        return False
    

    rows = Address.objects.filter(pk=address.pk).update(is_active=state, last_changed_by=requester)
    return True


def use_address_for_billing(address):
    if  not isinstance(address, Address):
        return False

    Address.objects.filter(pk=address.pk).update(address_type=Addressbook_Constants.ADDRESS_FOR_BILLING)
    return True


def use_address_for_shipping(address):
    if  not isinstance(address, Address):
        return False

    Address.objects.filter(pk=address.pk).update(address_type=Addressbook_Constants.ADDRESS_FOR_SHIPPING)
    return True


def use_address_for_billing_and_shipping(address):
    if  not isinstance(address, Address):
        return False

    Address.objects.filter(pk=address.pk).update(address_type=Addressbook_Constants.ADDRESS_FOR_BILLING_AND_SHIPPING)
    return True


def set_address_type(address, address_type):
    if  not isinstance(address, Address):
        return False

    if  not isinstance(address_type, int):
        return False
    
    k,v = utils.find_element_by_key_in_tuples(address_type, Addressbook_Constants.ADDRESS_TYPES)
    if v is None:
        return False

    Address.objects.filter(pk=address.pk).update(address_type=address_type)
    return True

def toggle_favorite(address):
    if  not isinstance(address, Address):
        return False
    
    Address.objects.filter(pk=address.pk).update(is_favorite=not F('is_favorite'))
    return True

def create_address(data):
    return core_tools.create_instance(model=Address, data=data)

def update_address(address, data):
    updated_address = core_tools.update_instance(model=Address, instance=address, data=data)
    if updated_address:
        logger.info("Address updated")
    
    return updated_address


def delete_address(address):
    if  not isinstance(address, Address):
        return False

    Address.objects.filter(pk=address.pk).delete()
    return True