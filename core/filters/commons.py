import numbers
import datetime
import uuid
import re

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
    FILTER_DATE_RANGE               : '__date__range',
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

FILTER_FIELD_LOOKUP_PREFIX          = "fl_"
FILTER_FIELD_PREFIX                 = 'ff_'
FILTER_FIELD_TYPE                   = ''

GROUP_PREFIX                        = "prefix"
GROUP_FIELD_NAME                    = "field_name"
INTEGER_PATTERN_REGEX               = re.compile(r'^[0-9]+$')
FIELD_PATTERN                       = re.compile(rf'(?P<{GROUP_PREFIX}>{FILTER_FIELD_PREFIX})(?P<{GROUP_FIELD_NAME}>\w+)')