
from django.db import models
from django.db.models import Q, F
from django.http.request import QueryDict
from core.filters import commons
from core.filters import field_filters
import numbers
import datetime
import uuid
import logging
import re

logger = logging.getLogger(__name__)



FILTER_TYPE_MAPPING = {
    'CharField' : field_filters.StringFieldFilter,
    'IntegerField': field_filters.IntegerFieldFilter,
    'Boolean' : field_filters.BooleanFieldFilter,
    'FloatField' : field_filters.FloatFieldFilter,
    'DateField' : field_filters.DateFieldFilter,
    'DateTimeField' : field_filters.DateTimeFieldFilter,
    'DecimalField': field_filters.DecimalFieldFilter,
    'UUIDField' : uuid.UUID,
    'TextField' : field_filters.StringFieldFilter,
    'ForeignKey' : field_filters.IntegerFieldFilter,
}



class Filter():

    def __init__(self, model, queryDict):

        if type(models.Model) != type(model):
            msg = f"Filter : model must be of the type of {type(models.Model)}. Current type is {type(model)}"
            logger.warn(msg)
            raise TypeError(msg)

        if not isinstance(queryDict, QueryDict):
            msg = f"Filter : queryDict must be of the type {type(QueryDict())}. Current type is {type(queryDict)}"
            logger.warn(msg)
            raise TypeError(msg)

        self.filters = []
        self.model = model
        self.queryDict = queryDict
        self.queryset = None
        self.filter_ready = False
    
    def __str__(self):
        return f"Filter for model {self.model} - queryDict : {self.queryDict}"
    
    
    def __repr__(self):
        return f"Filter for model {self.model} - queryDict : {self.queryDict}"
    

    def get_field_filter(self, field_name):
        attr = getattr(self.model, field_name, None)
        if attr is None:
            logger.debug(f"Model has no field {field_name}")
            return None

        return FILTER_TYPE_MAPPING.get(attr.field.get_internal_type(), None)

    
    def prepare_filters(self):
        q = {}
        selected_values = {}
        for key in self.queryDict:
            if not isinstance(key, str):
                continue
            #match = commons.FIELD_PATTERN.match(key)
            match = commons.FILTER_PATTERN.match(key)
            if not match:
                logger.debug("field not matched")
                continue
            field_name = match.group(commons.FIELD_NAME)
            FILTER_CLASS = self.get_field_filter(field_name)

            if FILTER_CLASS is None:
                logger.debug(f"No Filter class found for field {field_name}")
                continue
            self.add_filter(FILTER_CLASS(model=self.model, field_name=field_name, key=key, value=self.queryDict.get(key)))

    
    def add_filter(self, f_filter):
        if not issubclass(type(f_filter), field_filters.FieldFilter) :
            raise TypeError(f"f_filter is not of the type field_filters.FieldFilter. Current Type is {type(f_filter)}")
        self.filters.append(f_filter)
    
    def remove_filter(self, f_filter):
        if not issubclass(type(f_filter), field_filters.FieldFilter.__class__) :
            raise TypeError(f"f_filter is not of the type field_filters.FieldFilter. Current Type is {type(f_filter)}")
        self.filters.remove(f_filter)
    
    def apply_filter(self):
        self.prepare_filters()
        query_objects = Q()
        for f in self.filters:
            query_objects &= f.get_query()
        
        return self.model.objects.filter(query_objects)


    
def field_filter(model, queryDict):
    if type(models.Model) != type(model):
        return None, {}

    if not queryDict or not isinstance(queryDict, QueryDict):
        logger.warn(f"field_filter: error on queryDict : type of queryDict : \"{type(queryDict)}\"")
        return None, {}
    
    q = {}
    selected_values = {}

    for key in queryDict:
        if not isinstance(key, str):
            continue
        match = commons.FIELD_PATTERN.match(key)
        if not match:
            logger.debug("field not matched")
            continue
        field_name = match.group(commons.GROUP_FIELD_NAME)
        attr = getattr(model, field_name, None)
        if attr is None:
            logger.debug(f"Model has no field {field_name}")
            continue

        field_type = INTERNAL_TYPE_MAPPING [attr.field.get_internal_type()]
        values = list(filter( lambda k: k != '',queryDict.getlist(key)))

        values_len = len(values)
        if values_len == 0:
            logger.debug("no values found")
            continue
        values = list(map(field_type, values))

        fl_value = queryDict.get(commons.FILTER_FIELD_LOOKUP_PREFIX + field_name, '')
        if fl_value == '':
            fl_value = commons.FILTER_INTEGER_EQ
        else:
            fl_value = int(fl_value)
        
        if values_len == 1 and fl_value != commons.FILTER_INTEGER_RANGE :
            values = values[0]
        q[field_name + commons.FILTER_FIELD_LOOKUP[fl_value]] = values
        selected_values[field_name] = values

    return model.objects.filter(**q), selected_values

    
    