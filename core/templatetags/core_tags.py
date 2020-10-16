from django import template
import logging

logger = logging.getLogger(__name__)
register = template.Library()


@register.filter
def access_dict(_dict, key):
    if isinstance(_dict, dict) :
        return _dict.get(key, None)
    return None
