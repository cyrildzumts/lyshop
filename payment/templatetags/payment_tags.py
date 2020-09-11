from django import template
from lyshop import utils
from payment import conf
import logging

logger = logging.getLogger(__name__)


register = template.Library()



@register.filter
def declined_reason_key(value):
    k,v = conf.get_declined_reason_key(value)
    if k is None:
        logger.info(f"declined_reason_key : Could not found key  for value \"{value}\"")
        return value
    return k

@register.filter
def declined_reason_value(key):
    k,v = conf.get_declined_reason_value(key)
    if v is None:
        logger.info(f"declined_reason_value : Could not found value  for key \"{key}\"")
        return key
    return v


@register.filter
def payment_status_key(value):
    k,v = conf.get_payment_status_key(value)
    if k is None:
        logger.info(f"payment_status_key : Could not found key  for value \"{value}\"")
        return value
    return k

@register.filter
def payment_status_value(key):
    k,v = conf.get_payment_status_value(key)
    if v is None:
        logger.info(f"payment_status_value : Could not found value  for key \"{key}\"")
        return key
    return v



@register.filter
def payment_mode_key(value):
    k,v = conf.get_payment_mode_key(value)
    if k is None:
        logger.info(f"payment_mode_key : Could not found key  for value \"{value}\"")
        return value
    return k

@register.filter
def payment_mode_value(key):
    k,v = conf.get_payment_mode_value(key)
    if v is None:
        logger.info(f"payment_mode_value : Could not found value  for key \"{key}\"")
        return key
    return v



@register.filter
def payment_date_key(value):
    k,v = conf.get_payment_date_key(value)
    if k is None:
        logger.info(f"payment_date_key : Could not found key  for value \"{value}\"")
        return value
    return k

@register.filter
def payment_date_value(key):
    k,v = conf.get_payment_date_value(key)
    if v is None:
        logger.info(f"payment_date_value : Could not found value  for key \"{key}\"")
        return key
    return v