from django import template
from lyshop import utils
from shipment import constants as Constants

register = template.Library()


@register.filter
def tuple_key(value):
    k,v = utils.find_element_by_value_in_tuples(value, Constants.SHIPMENT_STATUS)
    if k is None:
        return value
    return k

@register.filter
def tuple_value(key):
    k,v = utils.find_element_by_key_in_tuples(key, Constants.SHIPMENT_STATUS)
    if v is None:
        return key
    return v