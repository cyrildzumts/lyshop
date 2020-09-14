

from addressbook.models import Address
import logging
import uuid

logger = logging.getLogger(__name__)


def get_addresses(user):
    if  not isinstance(user, User):
        return None
    return Address.objects.filter(user=user)


def toggle_address_active(address, requester, state):
    if  not isinstance(requester, User):
        return False
    if  not isinstance(address, Address):
        return False

    if  not isinstance(state, bool):
        return False
    

    rows = Address.objects.filter(pk=address.pk).update(is_active=state, last_changed_by=requester)
    return True


def delete_address(address):
    if  not isinstance(address, Address):
        return False
    Address.objects.filter(pk=address.pk).delete()
    return True