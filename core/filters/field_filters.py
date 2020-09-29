from django.db import models
from django.core.exceptions import FieldDoesNotExist
from django.db.models import Q, F
import time


def model_has_field(model, field_name):
    if type(models.Model) != type(model):
        return False
    
    found = False
    start = time.time()
    
    for field in model._meta.get_fields():
        if field.name == field_name:
            found = True
            break

    end = time.time() - start
    print("field check for loop in get_fields() : %.2f seconds", end)
    start = time.time()
    try:
        f = model._meta.get_field(field_name)
        found = True
    except FieldDoesNotExist as identifier:
        found = False
    end = time.time() - start
    print("field check get_field(): %.2f seconds", end)

    start = time.time()
    found = hasattr(Product, field_name)
    end = time.time() - start
    print("field check hasattr: %.2f seconds", end)

    start = time.time()
    found = getattr(Product, field_name, None)
    end = time.time() - start
    print("field check getattr: %.2f seconds", end)
    return False

def get_internal_type(model, field_name):
    pass

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