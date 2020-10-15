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
FILTER_IN                           = 6

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
FILTER_RANGE                        = 24


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
    (FILTER_INTEGER_LT, 'FILTER VALUE LESS THAN'),
    (FILTER_INTEGER_LTE, 'FILTER VALUE LESS THAN OR EQUAL'),
    (FILTER_INTEGER_EQ,  'FILTER VALUE EQUAL'),
    (FILTER_INTEGER_NEQ, 'FILTER VALUE NOT EQUAL'),
    (FILTER_IN, 'FILTER VALUE IN RANGE'),
)

FILTER_STRING_OPTIONS = (
    (FILTER_STRING_EXACT, 'FILTER STRING CONTENT EQUAL'),
    (FILTER_STRING_IEXACT, 'FILTER STRING CONTENT IGNORE CASE EQUAL'),
    (FILTER_STRING_CONTAINS, 'FILTER STRING CONTENT CONTAINS'),
    (FILTER_STRING_ICONTAINS, 'FILTER STRING CONTENT CONTAINS IGNORE CASE'),
)

FILTER_RANGE_OPTIONS = (
    (FILTER_RANGE, "FILTER VALUE IN RANGE"),
)

FILTER_FIELD_LOOKUP = {
    FILTER_INTEGER_GT               : '__gt',
    FILTER_INTEGER_GTE              : '__gte',
    FILTER_INTEGER_LT               : '__lt',
    FILTER_INTEGER_LTE              : '__lte',
    FILTER_INTEGER_EQ               : '',
    FILTER_IN                       : '__in',
    FILTER_STRING_EXACT             : '__exact',
    FILTER_STRING_IEXACT            : '__iexact',
    FILTER_STRING_CONTAINS          : '__contains',
    FILTER_STRING_ICONTAINS         : '__icontains',
    FILTER_DATE_BEFORE              : '__lt',
    FILTER_DATE_AFTER               : '__gt',
    FILTER_DATE_RANGE               : '__range',
    FILTER_DATE_YEAR                : '__year',
    FILTER_DATE_YEAR_AFTER          : '__year__gte',
    FILTER_DATE_YEAR_BEFORE         : '__year__lte',
    FILTER_DATE_MONTH               : '__month',
    FILTER_DATE_MONTH_AFTER         : '__month__gte',
    FILTER_DATE_MONTH_BEFORE        : '__month__lte',
    FILTER_DATE_DAY                 : '__day',
    FILTER_DATE_DAY_AFTER           : '__day__gte',
    FILTER_DATE_DAY_BEFORE          : '__day__lte',
    FILTER_RANGE                    : '__range',

}

INTERNAL_TYPE_MAPPING = {
    'CharField' : str,
    'IntegerField': int,
    'BooleanField' : bool,
    'FloatField' : float,
    'DateField' : datetime.date,
    'DateTimeField' : datetime.datetime,
    'DecimalField': float,
    'UUIDField' : uuid.UUID,
    'TextField' : str,
    'ForeignKey' : int,
}


QUERY_VALUE_SEPARATOR               = ","
QUERY_RANGE_SEPARATOR               = "-"
FILTER_FIELD_LOOKUP_PREFIX          = "fl__"
FILTER_FIELD_PREFIX                 = 'ff__'
FILTER_FIELD_TYPE                   = ''

GROUP_PREFIX                        = "prefix"
GROUP_SUFFIX                        = "suffix"
FIELD_NAME                          = "field_name"
RANGE_END_PREFIX                    = "max"
RANGE_START_PREFIX                  = "min"

MAX_VALUE                           = "max"
MIN_VALUE                           = "min"
RANGE_FILTER                        = "range"
INTEGER_PATTERN_REGEX               = re.compile(r'^[0-9]+$')
INTEGER_LIST_FILTER_PATTERN         = re.compile(r'^\d+([,;]\d+)*$')
INTEGER_RANGE_FILTER_PATTERN        = re.compile(r'(?P<START>\d+)?(?:-{1,2})(?P<END>\d+)?')
UUID_PATTERN_REGEX                  = re.compile(r'^[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$')
DATE_PATTERN_REGEX                  = re.compile(r'^$')
DATETIME_PATTERN_REGEX              = re.compile(r'^$')
BOOLEAN_PATTERN_REGEX               = re.compile(r'^(?i)(?P<TRUE>true|on|yes|1)|(?P<FALSE>false|off|no|0)$')
DECIMAL_PATTERN_REGEX               = re.compile(r'^\d+([.]\d+)?$')
DECIMAL_LIST_PATTERN                = re.compile(r'^(\d+([.]\d+)?)+(,(\d+([.]\d+)?))*$')

VALUES_IN_FILTER_PATTERN            = re.compile(r'^\d+([,;]\d+)*$')
RANGE_FILTER_PATTERN                = re.compile(r'(?P<START>\d+)?(?:-{1,2})(?P<END>\d+)?')
DECIMAL_RANGE_FILTER_PATTERN        = re.compile(r'^(?P<START>(?:\d+(?:[.]\d+)?))(?:-{1,2})(?P<END>(?:\d+(?:[.]\d+)?))$')
#FIELD_PATTERN                       = re.compile(rf'(?P<{GROUP_PREFIX}>{FILTER_FIELD_PREFIX})(?P<{GROUP_FIELD_NAME}>[0-9a-zA-Z]+|[0-9a-zA-Z]+_[0-9a-zA-Z]+)(?:__(?P<{RANGE_FILTER}>{RANGE_MIN_PEFIX}|{RANGE_MAX_PREFIX}))?')
FIELD_PATTERN = re.compile(rf'(?P<{GROUP_PREFIX}>{FILTER_FIELD_PREFIX})(?P<{FIELD_NAME}>(?:(?:[a-z][0-9a-zA-Z]*(?:_[0-9a-zA-Z]+)*)))(?:(?:__)(?P<{RANGE_FILTER}>{RANGE_START_PREFIX}-{RANGE_END_PREFIX}))?')
# fieldname is valid; field_name is valid ; field_name_extra is valid, fieldname__max is valid, fieldname_min is valid.
FILTER_PATTERN = re.compile(rf'(?P<{FIELD_NAME}>(?:(?:[a-z][0-9a-zA-Z]*(?:_[0-9a-zA-Z]+)*)))(?:(?:__)(?P<{GROUP_SUFFIX}>{MAX_VALUE}|{MIN_VALUE}))?')
