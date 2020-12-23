from django import template
from lyshop import utils
from shipment import constants as Constants
import logging

logger = logging.getLogger(__name__)


register = template.Library()


@register.filter
def shipment_status_key(value):
    k,v = utils.find_element_by_value_in_tuples(value, Constants.SHIPMENT_STATUS)
    if k is None:
        logger.info(f" shipment_status_key : Could not found key  for value \"{value}\"")
        return value
    return k

@register.filter
def shipment_status_value(key):
    k,v = utils.find_element_by_key_in_tuples(key, Constants.SHIPMENT_STATUS)
    if v is None:
        logger.info(f"shipment_status_value : Could not found value for key \"{key}\"")
        return key
    return v



@register.filter
def ship_mode_value(key):
    k,v = utils.find_element_by_key_in_tuples(key, Constants.SHIP_MODE)
    if v is None:
        logger.info(f"ship_mode_value : Could not found value for key \"{key}\"")
        return key
    return v