
from django.db import models
from django.db.models import Q, F
from django.http import QueryDict
import logging

logger = logging.getLogger(__name__)

FILTER_INTEGER_GT                   = 0
FILTER_INTEGER_GTE                  = 1
FILTER_INTEGER_LT                   = 2
FILTER_INTEGER_LTE                  = 3
FILTER_INTEGER_EQ                   = 4
FILTER_INTEGER_NEQ                  = 5
FILTER_INTEGER_RANGE                = 6

FILTER_STRING_EXACT                 = 7
FILTER_STRING_IEXACT                = 8
FILTER_STRING_CONTAINS              = 9
FILTER_STRING_ICONTAINS             = 10

FILTER_DATE_BEFORE                  = 11
FILTER_DATE_AFTER                   = 12
FILTER_DATE_RANGE                   = 13
FILTER_DATE_YEAR                    = 14
FILTER_DATE_YEAR_BEFORE             = 15
FILTER_DATE_YEAR_AFTER              = 16
FILTER_DATE_MONTH                   = 17
FILTER_DATE_MONTH_BEFORE            = 18
FILTER_DATE_MONTH_AFTER             = 19
FILTER_DATE_DAY                     = 20
FILTER_DATE_DAY_BEFORE              = 21
FILTER_DATE_DAY_AFTER               = 22
FILTER_DATE_DATE                    = 23


FILTER_DATE_OPTIONS = (
    (FILTER_DATE_BEFORE, 'FILTER DATE BEFORE'),
    (FILTER_DATE_AFTER, 'FILTER DATE AFTER'),
    (FILTER_DATE_RANGE, 'FILTER DATE IN RANGE'),
    (FILTER_DATE_YEAR, 'FILTER DATE ON YEAR'),
    (FILTER_DATE_YEAR_BEFORE, 'FILTER DATE ON YEAR BEFORE'),
    (FILTER_DATE_YEAR_AFTER, 'FILTER DATE ON YEAR AFTER'),
    (FILTER_DATE_MONTH, 'FILTER DATE ON MONTH'),
    (FILTER_DATE_MONTH_BEFORE, 'FILTER DATE ON MONTH BEFORE'),
    (FILTER_DATE_MONTH_AFTER, 'FILTER DATE ON MONTH AFTER'),
    (FILTER_DATE_DAY, 'FILTER DATE ON DAY'),
    (FILTER_DATE_DAY_BEFORE, 'FILTER DATE ON DAY BEFORE'),
    (FILTER_DATE_DAY_AFTER, 'FILTER DATE ON DAY AFTER'),
)

FILTER_INTEGER_OPTIONS = (
    (FILTER_INTEGER_GT, 'FILTER VALUE GREATER THAN'),
    (FILTER_INTEGER_GTE, 'FILTER VALUE GREATER THAN OR EQUAL'),
    (FILTER_INTEGER_LT, 'FILTER VALUE LOWER THAN'),
    (FILTER_INTEGER_LTE, 'FILTER VALUE LOWER THAN OR EQUAL'),
    (FILTER_INTEGER_EQ,  'FILTER VALUE EQUAL'),
    (FILTER_INTEGER_NEQ, 'FILTER VALUE NOT EQUAL'),
    (FILTER_INTEGER_RANGE, 'FILTER VALUE IN RANGE'),
)

FILTER_STRING_OPTIONS = (
    (FILTER_STRING_EXACT, 'FILTER STRING CONTENT EQUAL'),
    (FILTER_STRING_IEXACT, 'FILTER STRING CONTENT IGNORE CASE EQUAL'),
    (FILTER_STRING_CONTAINS, 'FILTER STRING CONTENT CONTAINS'),
    (FILTER_STRING_ICONTAINS, 'FILTER STRING CONTENT CONTAINS IGNORE CASE'),
)

FILTER_FIELD_LOOKUP = {
    FILTER_INTEGER_GT               : '__gt',
    FILTER_INTEGER_GTE              : '__gte',
    FILTER_INTEGER_LT               : '__lt',
    FILTER_INTEGER_LTE              : '__lte',
    FILTER_INTEGER_EQ               : '',
    FILTER_INTEGER_RANGE            : '__in',
    FILTER_STRING_EXACT             : '__exact',
    FILTER_STRING_IEXACT            : '__iexact',
    FILTER_STRING_CONTAINS          : '__contains',
    FILTER_STRING_ICONTAINS         : '__icontains',
    FILTER_DATE_BEFORE              : '__date__lt',
    FILTER_DATE_AFTER               : '__date__gt',
    FILTER_DATE_IN_RANGE            : '__date__range',
    FILTER_DATE_YEAR                : '__year',
    FILTER_DATE_YEAR_AFTER          : '__year__gte',
    FILTER_DATE_YEAR_BEFORE         : '__year__lte',
    FILTER_DATE_MONTH               : '__month',
    FILTER_DATE_MONTH_AFTER         : '__month__gte',
    FILTER_DATE_MONTH_BEFORE        : '__month__lte',
    FILTER_DATE_DAY                 : '__day',
    FILTER_DATE_DAY_AFTER           : '__day__gte',
    FILTER_DATE_DAY_BEFORE          : '__day__lte',

}

FILTER_FIELD_LOOKUP_PREFIX          = "fl_"
FILTER_FIELD_PREFIX                 = 'ff_'
FILTER_FIELD_TYPE                   = ''

def get_query(key, queryDict):
    if not key not queryDict or not isinstance(queryDict, QueryDict) or not isinstance(key, str):
        logger.warn("get_query: error key or queryDict")
        return None
    q = {}
    v = queryDict.getlist(key)
    field_name = key[len(FILTER_FIELD_LOOKUP_PREFIX):None]
    fl_key = FILTER_FIELD_LOOKUP_PREFIX + name
    fl_value = queryDict.get(FILTER_FIELD_LOOKUP_PREFIX + name)
    q[field_name + FILTER_FIELD_LOOKUP[fl_value]] = v
    logger.debug(f"get_query(): {q}")
    return q




def extract_integer_filter(queryDict):
    if not queryDict or not isinstance(queryDict, QueryDict):
        logger.warn("extract_integer_filter: error on queryDict")
        return None
    query_search = {}
    for key in queryDict:
        if not isinstance(key, str):
            continue
        if key.startwith(FILTER_FIELD_PREFIX):
            query_search.update(get_query(key, queryDict))
    return query_search
    

def field_filter(model, queryDict):
    if type(models.Model) != type(model):
        return None
    
    filter_params = extract_integer_filter(queryDict)
    
    