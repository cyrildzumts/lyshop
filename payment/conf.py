from django.utils.translation import gettext_lazy as _
from lyshop import utils


PAYMENT_CASH = 0
PAYMENT_PAY = 1
PAYMENT_MOBILE = 2
PAYMENT_BANK_TRANSFER = 3


PAYMENT_MODE = (
    (PAYMENT_CASH, "CASH"),
    (PAYMENT_MOBILE, "MOBILE PAYMENT"),
    (PAYMENT_BANK_TRANSFER, "BANK TRANSFER"),
    (PAYMENT_PAY, "PAYMENT WITH PAY"),
)

PAYMENT_DATE_LAST_FRIDAY = 0
PAYMENT_DATE_FIRST_FRIDAY = 1

PAYMENT_DATE_NAME_CHOICES = [
    "PAYMENT ON LAST FRIDAY OF MONTH",
    "PAYMENT ON FIRST FRIDAY OF MONTH"
]

PAYMENT_DATE = (
    (PAYMENT_DATE_LAST_FRIDAY, PAYMENT_DATE_NAME_CHOICES[0]),
    (PAYMENT_DATE_FIRST_FRIDAY, PAYMENT_DATE_NAME_CHOICES[1])
)

def get_payment_mode_value(key):
    k, v = utils.find_element_by_key_in_tuples(key, PAYMENT_MODE)
    return k, v


def get_payment_mode_key(value):
    k, v = utils.find_element_by_value_in_tuples(value, PAYMENT_MODE)
    return k, v


def get_payment_date_value(key):
    k, v = utils.find_element_by_key_in_tuples(key, PAYMENT_DATE)
    return k, v


def get_payment_date_key(value):
    k, v = utils.find_element_by_value_in_tuples(value, PAYMENT_DATE)
    return k, v