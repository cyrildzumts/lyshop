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

    def __init__(self, model, field_name=None, values=None, action=None, key=None, value=None):
        
        if type(models.Model) != type(model):
            raise TypeError(f"Filter : model must be of the type of django.db.models.Model. Current type is {type(model)}")
        self.field_name_lookup = field_name
        self.key = key
        self.validate(value)
        self.value = value
        self.model = model
        self.field = getattr(self.model, field_name).field
        self.field_type = commons.INTERNAL_TYPE_MAPPING[self.field.get_internal_type()]
        self.action = action
        self.q = {}
        self.values = None
        

    
    def validate(self, values):
        raise NotImplementedError("validate() method is not implemented for this filter yet")


    def get_query(self):
        raise NotImplementedError("This method is not implemented for this filter yet")

    def prepare_filter(self):
        match = commons.FILTER_PATTERN.match(self.key)
        max_min = False
        if not match:
            logger.debug("field not matched")
            raise KeyError(f"Key {self.key} does not match any fieldname")
        
        try:
            suffix = match.group(commons.GROUP_SUFFIX)
        except IndexError as e:
            logger.warn(f"No suffix {commons.GROUP_SUFFIX} matched on the fieldname")
            suffix = ""
        
        if commons.MAX_VALUE == suffix:
            f_action = commons.FILTER_INTEGER_LTE
            max_min = True
        
        if commons.MIN_VALUE == suffix:
            f_action = commons.FILTER_INTEGER_GTE
            max_min = True
        if max_min:
            values = self.field_type(self.value)
            self.field_name_lookup += commons.FILTER_FIELD_LOOKUP.get(f_action)
        else:
            value = self.value
            if commons.VALUES_IN_FILTER_PATTERN.match(self.value):
                values = self.value.split(commons.QUERY_VALUE_SEPARATOR)
                values_len = len(values)
                if values_len > 1 :
                    f_action = commons.FILTER_IN
                    values = list(map(self.field_type, values))
                elif values_len == 1:
                    f_action = commons.FILTER_INTEGER_EQ
                    values = list(map(self.field_type, values))[0]     

            elif commons.RANGE_FILTER_PATTERN.match(self.value):
                values = list(map(self.field_type, self.value.split(commons.QUERY_RANGE_SEPARATOR)))
                f_action = commons.FILTER_RANGE
                values = (values[0], values[1])
            
        self.field_name_lookup += commons.FILTER_FIELD_LOOKUP.get(f_action)
        self.values = values
        self.q[self.field_name_lookup] =  self.values
        return self.q


class BooleanFieldFilter(FieldFilter):

    def __init__(self,  **kwargs):
        super().__init__(**kwargs)
    
    def get_query(self):
        logger.debug(f"{self.__class__.__name__} : get_query")
        return Q(**self.q)

    def validate(self, value):
        if not commons.BOOLEAN_PATTERN_REGEX.match(value):
            raise ValueError(f"Value {value} does not represent boolean values")
    
    def prepare_filter(self):
        value = self.value
        match = commons.BOOLEAN_PATTERN_REGEX.match(self.value)
        if not match:
            raise ValueError()

        self.values = value
        self.q[self.field_name_lookup] = match.group('TRUE') is not None
        return self.q


class IntegerFieldFilter(FieldFilter):

    def __init__(self,  **kwargs):
        super().__init__(**kwargs)

    def validate(self, value):
        if not commons.INTEGER_PATTERN_REGEX.match(value) and not commons.INTEGER_LIST_FILTER_PATTERN.match(value) and not commons.INTEGER_RANGE_FILTER_PATTERN.match(value):
            raise ValueError(f"Value {value} does not represent integer values")


    
    def get_query(self):
        logger.debug(f"{self.__class__.__name__} : get_query")
        
        return Q(**self.prepare_filter())


class FloatFieldFilter(FieldFilter):

    def __init__(self, range_start=None, range_end=None, **kwargs):
        super().__init__(**kwargs)
    
    def get_query(self):
        logger.debug(f"{self.__class__.__name__} : get_query")
        
        return Q(**self.prepare_filter())

    def validate(self, value):
        if not commons.DECIMAL_PATTERN_REGEX.match(value) and not commons.DECIMAL_LIST_PATTERN.match(value) and not commons.DECIMAL_RANGE_FILTER_PATTERN.match(value):
            raise ValueError(f"Value {value} does not represent float values")


class DecimalFieldFilter(FieldFilter):

    def __init__(self, range_start=None, range_end=None, **kwargs):
        super().__init__(**kwargs)

    
    def validate(self, value):
        if not commons.DECIMAL_PATTERN_REGEX.match(value) and not commons.DECIMAL_LIST_PATTERN.match(value) and not commons.DECIMAL_RANGE_FILTER_PATTERN.match(value):
            raise ValueError(f"Value {value} does not represent decimal values")
    
    def get_query(self):
        logger.debug(f"{self.__class__.__name__} : get_query")
        
        return Q(**self.prepare_filter())


class DateFieldFilter(FieldFilter):

    def __init__(self, range_start=None, range_end=None, option=None, **kwargs):
        super().__init__(**kwargs)
    
    def get_query(self):
        logger.debug(f"{self.__class__.__name__} : get_query")
        
        return Q(**self.prepare_filter())

    def validate(self, value):
        if not commons.DATE_PATTERN_REGEX.match(value):
            raise ValueError(f"Value {value} does not represent an Date values")


class DateTimeFieldFilter(FieldFilter):

    def __init__(self, range_start=None, range_end=None, option=None, **kwargs):
        super().__init__(**kwargs)
    
    def get_query(self):
        logger.debug(f"{self.__class__.__name__} : get_query")
        
        return Q(**self.prepare_filter())

    def validate(self, value):
        if not commons.DATETIME_PATTERN_REGEX.match(value):
            raise ValueError(f"Value {value} does not represent an DateTime values")



class StringFieldFilter(FieldFilter):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def get_query(self):
        logger.debug(f"{self.__class__.__name__} : get_query")

    def validate(self, value):
        return


class UUIDFieldFilter(FieldFilter):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    
    def get_query(self):
        logger.debug(f"{self.__class__.__name__} : get_query")
        
        return Q(**self.prepare_filter())

    
    def validate(self, value):
        if not commons.UUID_PATTERN_REGEX.match(value):
            raise ValueError(f"Value {value} does not represent an UUID values")



