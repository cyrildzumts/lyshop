from django.utils.translation import gettext_lazy as _
from lyshop import utils


PAYMENT_CASH = 0
PAYMENT_PAY = 1
PAYMENT_MOBILE = 2
PAYMENT_BANK_TRANSFER = 3

DECLINED_DATE_NOT_REACHED = 0
DECLINED_NO_PRODUCT_SOLD = 1
DECLINED_NO_PAY_USER_ID = 2
DECLINED_NO_MOBILE_NUMBER = 3
DECLINED_NO_BANKING_DATA = 4
DECLINED_REASON = (
    (DECLINED_DATE_NOT_REACHED, "PAYMENT DATE NOT REACHED"),
    (DECLINED_NO_PRODUCT_SOLD, "NO PRODUCT SOLD"),
    (DECLINED_NO_PAY_USER_ID, "PAY USER ID MISSING"),
    (DECLINED_NO_MOBILE_NUMBER, "MOBILE NUMBER MISSING"),
    (DECLINED_NO_BANKING_DATA, "BANKING DATA MISSING"),
)

PAYMENT_SUBMITTED = 0
PAYMENT_ACCEPTED = 1
PAYMENT_PAID = 2
PAYMENT_DECLINED = 3

PAYMENT_STATUS = (
    (PAYMENT_SUBMITTED, "SUBMITTED"),
    (PAYMENT_ACCEPTED, "ACCEPTED"),
    (PAYMENT_PAID, "PAID"),
    (PAYMENT_DECLINED, "DECLINED")
)


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


def get_declined_reason_value(key):
    k, v = utils.find_element_by_key_in_tuples(key, DECLINED_REASON)
    return k, v


def get_declined_reason_key(value):
    k, v = utils.find_element_by_value_in_tuples(value, DECLINED_REASON)
    return k, v

def get_payment_status_value(key):
    k, v = utils.find_element_by_key_in_tuples(key, PAYMENT_STATUS)
    return k, v


def get_payment_status_key(value):
    k, v = utils.find_element_by_value_in_tuples(value, PAYMENT_STATUS)
    return k, v


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