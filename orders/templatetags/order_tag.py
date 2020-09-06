from django import template
from lyshop import utils
from orders import commons as Constants
import logging

logger = logging.getLogger(__name__)


register = template.Library()


@register.filter
def order_status_key(value):
    k,v = utils.find_element_by_value_in_tuples(value, Constants.ORDER_STATUS)
    if k is None:
        logger.info(f"order_status_key : Could not found key  for value \"{value}\"")
        return value
    return k

@register.filter
def order_status_value(key):
    k,v = Constants.get_order_status_name(key)
    if v is None:
        logger.info(f"order_status_value : Could not found value  for key \"{key}\"")
        return key
    return v


@register.filter
def pay_option(value):
    k,v = Constants.get_payment_option_name(value)
    if k is None:
        logger.info(f"order_status_value : Could not found key  for value \"{value}\"")
        return value
    return k


@register.filter
def pay_status_key(value):
    k,v = utils.find_element_by_value_in_tuples(value, Constants.PAYMENT_STATUS)
    if k is None:
        logger.info(f"pay_status_key: Could not found key  for value \"{value}\"")
        return value
    return k