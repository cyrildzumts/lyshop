from django.db import models
from django.core.exceptions import FieldDoesNotExist
from django.db.models import Q, F
from core.filters import commons
import time
import numbers
import datetime
import uuid
import logging
import re

logger = logging.getLogger(__name__)


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


class FieldFilter():

    def __init__(self, model, field_name, values, action):
        
        if type(models.Model) != type(model):
            raise TypeError(f"Filter : model must be of the type of django.db.models.Model. Current type is {type(model)}")

        self.model = model
        self.field = getattr(self.model, field_name).field
        self.field_type = commons.INTERNAL_TYPE_MAPPING[self.field.get_internal_type()]
        self.action = action
        self.values = list(map(self.field_type, values))


    def get_query(self):
        raise NotImplementedError("This method is not implemented for this filter yet")





class BooleanFieldFilter(FieldFilter):

    def __init__(self,  **kwargs):
        super().__init__(**kwargs)
    
    def get_query(self):
        logger.debug(f"{self.__class__.__name__} : get_query")
        q = {
            self.field.name + commons.FILTER_FIELD_LOOKUP[self.action]: self.values
        }
        return Q(**q)

class IntegerFieldFilter(FieldFilter):

    def __init__(self, range_start=None, range_end=None, **kwargs):
        super().__init__(**kwargs)
        self.range_start = range_start
        self.range_end = range_end
    
    def get_query(self):
        logger.debug(f"{self.__class__.__name__} : get_query")
        if self.range_start and self.range_end:
            q = {
                self.field.name + commons.FILTER_FIELD_LOOKUP[commons.FILTER_RANGE]: (self.range_start, self.range_end)
            }
        else:
            q = {
                self.field.name + commons.FILTER_FIELD_LOOKUP[self.action]: self.values
            }
        return Q(**q)


class FloatFieldFilter(FieldFilter):

    def __init__(self, range_start=None, range_end=None, **kwargs):
        super().__init__(**kwargs)
    
    def get_query(self):
        logger.debug(f"{self.__class__.__name__} : get_query")
        if self.range_start and self.range_end:
            q = {
                self.field.name + commons.FILTER_FIELD_LOOKUP[commons.FILTER_RANGE]: (self.range_start, self.range_end)
            }
        else:
            q = {
                self.field.name + commons.FILTER_FIELD_LOOKUP[self.action]: self.values
            }
        return Q(**q)


class DecimalFieldFilter(FieldFilter):

    def __init__(self, range_start=None, range_end=None, **kwargs):
        super().__init__(**kwargs)
    
    def get_query(self):
        logger.debug(f"{self.__class__.__name__} : get_query")
        if self.range_start and self.range_end:
            q = {
                self.field.name + commons.FILTER_FIELD_LOOKUP[commons.FILTER_RANGE]: (self.range_start, self.range_end)
            }
        else:
            q = {
                self.field.name + commons.FILTER_FIELD_LOOKUP[self.action]: self.values
            }
        return Q(**q)


class DateFieldFilter(FieldFilter):

    def __init__(self, range_start=None, range_end=None, option=None, **kwargs):
        super().__init__(**kwargs)
    
    def get_query(self):
        logger.debug(f"{self.__class__.__name__} : get_query")
        if self.range_start and self.range_end:
            q = {
                self.field.name + commons.FILTER_FIELD_LOOKUP[commons.FILTER_RANGE]: (self.range_start, self.range_end)
            }
        else:
            q = {
                self.field.name + commons.FILTER_FIELD_LOOKUP[self.action]: self.values
            }
        return Q(**q)


class DateTimeFieldFilter(FieldFilter):

    def __init__(self, range_start=None, range_end=None, option=None, **kwargs):
        super().__init__(**kwargs)
    
    def get_query(self):
        logger.debug(f"{self.__class__.__name__} : get_query")
        if self.range_start and self.range_end:
            q = {
                self.field.name + commons.FILTER_FIELD_LOOKUP[commons.FILTER_RANGE]: (self.range_start, self.range_end)
            }
        else:
            q = {
                self.field.name + commons.FILTER_FIELD_LOOKUP[self.action]: self.values
            }
        return Q(**q)



class StringFieldFilter(FieldFilter):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def get_query(self):
        logger.debug(f"{self.__class__.__name__} : get_query")


class UUIDFieldFilter(FieldFilter):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    
    def get_query(self):
        logger.debug(f"{self.__class__.__name__} : get_query")



