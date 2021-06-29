from django import template
from django.utils.translation import gettext_lazy as _
from lyshop import utils
from catalog import constants as Constants
from catalog import catalog_service
import logging

logger = logging.getLogger(__name__)


register = template.Library()



@register.simple_tag
def core_trans (value):
    if isinstance(value, str):
        return _(value)
    return value


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
    return _(v)




@register.filter
def attr_type_key(value):
    k,v = utils.find_element_by_value_in_tuples(value, Constants.ATTRIBUTE_TYPE)
    if k is None:
        logger.info(f"attr_type_key : Could not found key  for value \"{value}\"")
        return value
    return k


@register.filter
def attr_type_value(key):
    k,v = utils.find_element_by_key_in_tuples(key, Constants.ATTRIBUTE_TYPE)
    if v is None:
        logger.info(f"attr_type_value : Could not found value  for key \"{key}\"")
        return key
    return _(v)


@register.filter
def category_page_title(key):
    k,v = utils.find_element_by_key_in_tuples(key, Constants.CATEGORIES)
    if v is None:
        logger.info(f"category_page_title : Could not found value  for key \"{key}\"")
        return key
    return v

@register.inclusion_tag("tags/navigation_tree.html")
def nav_tree(category):
    categories_map = category.children
    logger.info("nav_tree tags")
    return {"categories_map": categories_map}