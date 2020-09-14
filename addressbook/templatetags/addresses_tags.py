from django import template
from lyshop import utils
from addressbook import constants as Constants
import logging

logger = logging.getLogger(__name__)


register = template.Library()


@register.filter
def address_type_key(value):
    k,v = utils.find_element_by_value_in_tuples(value, Constants.ADDRESS_TYPES)
    if k is None:
        logger.info(f"address_type_key : Could not found key  for value \"{value}\"")
        return value
    return k

@register.filter
def address_type_value(key):
    k,v = utils.find_element_by_key_in_tuples(key, Constants.ADDRESS_TYPES)
    if v is None:
        logger.info(f"address_type_value : Could not found value  for key \"{key}\"")
        return key
    return v