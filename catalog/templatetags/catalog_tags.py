from django import template
from lyshop import utils
from catalog import constants as Constants
import logging

logger = logging.getLogger(__name__)


register = template.Library()



@register.filter
def gender_key(value):
    k,v = Constants.get_gender_key(value)
    if k is None:
        logger.info(f"gender_key : Could not found key  for value \"{value}\"")
        return value
    return k


@register.filter
def gender_value(key):
    k,v = Constants.get_gender_value(key)
    if v is None:
        logger.info(f"gender_value : Could not found value  for key \"{key}\"")
        return key
    return v




@register.filter
def attr_type_key(value):
    k,v = Constants.get_attribute_type_key(value)
    if k is None:
        logger.info(f"attr_type_key : Could not found key  for value \"{value}\"")
        return value
    return k


@register.filter
def attr_type_value(key):
    k,v = Constants.get_attribute_type_value(key)
    if v is None:
        logger.info(f"attr_type_value : Could not found value  for key \"{key}\"")
        return key
    return v