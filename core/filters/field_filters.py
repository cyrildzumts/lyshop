from django.db import models
from django.core.exceptions import FieldDoesNotExist
from django.db.models import Q, F
import time


def model_has_field(model, field_name):
    if type(models.Model) != type(model):
        return False

    return getattr(model, field_name, None) is not None


def get_internal_type(model, field_name):
    if type(models.Model) != type(model):
        return ""
    
    attr = getattr(model, field_name, None)
    if attr is not None:
        return attr.field.get_internal_type()
    return ""
    

def integer_field_filter(field_name, field_values, filter_lookup):
    return {}

def string_field_filter(field_name, field_values, filter_lookup):
    return {}

def float_field_filter(field_name, field_values, filter_lookup):
    return {}

def date_field_filter(field_name, field_values, filter_lookup):
    return {}

def datetime_field_filter(field_name, field_values, filter_lookup):
    return {}

def uuid_field_filter(field_name, field_values, filter_lookup):
    return {}