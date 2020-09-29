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
    print(f"field check for loop in get_fields() : {end:.6f} seconds")
    start = time.time()
    try:
        f = model._meta.get_field(field_name)
        found = True
    except FieldDoesNotExist as identifier:
        found = False
    end = time.time() - start
    print(f"field check get_field(): {end:.6f} seconds")

    start = time.time()
    found = hasattr(model, field_name)
    end = time.time() - start
    print(f"field check hasattr: {end:.6f} seconds")

    start = time.time()
    found = getattr(model, field_name, None)
    end = time.time() - start
    print(f"field check getattr: {end:.6f} seconds")
    return found

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