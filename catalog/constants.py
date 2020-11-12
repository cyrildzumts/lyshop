
from lyshop import utils
import datetime
import re


SHORT_DESCRIPTION_MAX_SIZE = 164
DESCRIPTION_MAX_SIZE = 300

GENDER_MEN          = 1
GENDER_WOMEN        = 2
GENDER_BABY_GIRL    = 3
GENDER_BABY_BOY     = 4
GENDER_GIRL         = 5
GENDER_BOY          = 6
GENDER_NO_GENDER    = 7


CHILDREN = (
    (GENDER_BOY, 'BOY'),
    (GENDER_GIRL, 'GIRL')
)

BABY = (
    (GENDER_BABY_BOY, 'BABY BOY'),
    (GENDER_BABY_GIRL, 'BABY GIRL')
)

GENDER = (
        (GENDER_MEN, 'MEN'),
        (GENDER_WOMEN, 'WOMEN'),
        (GENDER_BABY_GIRL, 'BABY GIRL'),
        (GENDER_BABY_BOY, 'BABY BOY'),
        (GENDER_GIRL, 'GIRL'),
        (GENDER_BOY, 'BOY'),
        (GENDER_NO_GENDER, 'NO GENDER')
    )

GENDER_OLD = (
    ('MEN', GENDER_MEN),
    ('WOMEN', GENDER_WOMEN),
    ('BABY GIRL', GENDER_BABY_GIRL),
    ('BABY BOY', GENDER_BABY_BOY),
    ('GIRL', GENDER_GIRL),
    ('BOY', GENDER_BOY),
    ('NO GENDER', GENDER_NO_GENDER)
)

ATTRIBUTE_TYPE_STRING = 1
ATTRIBUTE_TYPE_INTEGER = 2
ATTRIBUTE_TYPE_DECIMAL = 3
ATTRIBUTE_TYPE_DATE   = 4
ATTRIBUTE_TYPE_DATETIME = 5
ATTRIBUTE_TYPE_DEFAULT = ATTRIBUTE_TYPE_STRING

ATTRIBUTE_TYPE = (
    (ATTRIBUTE_TYPE_STRING, 'STRING'),
    (ATTRIBUTE_TYPE_INTEGER, 'INTEGER'),
    (ATTRIBUTE_TYPE_DECIMAL, 'DECIMAL'),
    (ATTRIBUTE_TYPE_DATE, 'DATE'),
    (ATTRIBUTE_TYPE_DATETIME, 'DATETIME')
)

ATTRIBUTE_TYPE_MAPPING = {
    ATTRIBUTE_TYPE_STRING : str,
    ATTRIBUTE_TYPE_INTEGER : int,
    ATTRIBUTE_TYPE_DECIMAL : float,
    ATTRIBUTE_TYPE_DATETIME : datetime.datetime,
    ATTRIBUTE_TYPE_DATE : datetime.date
}

ATTRIBUTE_TYPE_OLD = (
    ('STRING', ATTRIBUTE_TYPE_STRING),
    ('INTEGER', ATTRIBUTE_TYPE_INTEGER),
    ('DECIMAL', ATTRIBUTE_TYPE_DECIMAL),
    ('DATE', ATTRIBUTE_TYPE_DATE),
    ('DATETIME', ATTRIBUTE_TYPE_DATETIME),
    ('DEFAULT(STRING)', ATTRIBUTE_TYPE_DEFAULT)
)

COMMISSION_DEFAULT = 0.03
COMMISSION_MAX_DIGITS = 7
COMMISSION_DECIMAL_PLACES = 5

DEFAULT_PRIMARY_ATTRIBUTES = ['size', 'capacity','color']

INTEGER_PATTERN_REGEX               = re.compile(r'^[0-9]+$')
LIST_FILTER_PATTERN                 = re.compile(r'^\w+([,;]\w+)*$')
INTEGER_RANGE_FILTER_PATTERN        = re.compile(r'(?P<START>\d+)?(?:-{1,2})(?P<END>\d+)?')


def get_attribute_type_key(value):
    return utils.find_element_by_value_in_tuples(value, ATTRIBUTE_TYPE)

def get_gender_key(value):
    return utils.find_element_by_value_in_tuples(value, GENDER)


def get_attribute_type_value(key):
    return utils.find_element_by_key_in_tuples(key, ATTRIBUTE_TYPE)

def get_gender_value(key):
    return utils.find_element_by_key_in_tuples(key, GENDER)
