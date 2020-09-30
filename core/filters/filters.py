
from django.db import models
from django.db.models import Q, F
from django.http import QueryDict
from core.filters import commons
from core.filters import field_filters
import numbers
import datetime
import uuid
import logging
import re

logger = logging.getLogger(__name__)



INTERNAL_TYPE_MAPPING = {
    'CharField' : str,
    'IntegerField': int,
    'Boolean' : bool,
    'FloatField' : float,
    'DateField' : datetime.date,
    'DateTimeField' : datetime.datetime,
    'DecimalField': float,
    'UUIDField' : uuid.UUID,
    'TextField' : str,
    'ForeignKey' : int,
}


    
def field_filter(model, queryDict):
    if type(models.Model) != type(model):
        return None

    if not queryDict or not isinstance(queryDict, QueryDict):
        logger.warn("field_filter: error on queryDict")
        return None
    
    q = {}

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
        values = queryDict.getlist(key)
        values_len = len(values)
        if values_len == 0:
            logger.debug("no values found")
            continue
        if values_len > 1:
            values = list(map(field_type, values))
        if values_len == 1:
            values = field_type(values[0])

        fl_value = queryDict.get(commons.FILTER_FIELD_LOOKUP_PREFIX + field_name, '')
        if fl_value == '':
            fl_value = commons.FILTER_INTEGER_EQ
        else:
            fl_value = int(fl_value)
        q[field_name + commons.FILTER_FIELD_LOOKUP[fl_value]] = values

    logger.debug(f'field_filter: {q}')
    return model.objects.filter(**q)

    
    