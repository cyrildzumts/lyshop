import timeit
import itertools
from lyshop import utils

PAYMENT_PAY_AT_DELIVERY = 0
PAYMENT_PAY_WITH_PAY = 1
PAYMENT_PAY_TOKEN = None
PAYMENT_PAY_USER = None
PAYMENT_PAY_HOST = 'http://pay-atalaku.com/api/payment-request'
PAYMENT_PAY_URL = f'{PAYMENT_PAY_HOST}/{PAYMENT_PAY_USER}/{PAYMENT_PAY_TOKEN}/'



PR_ACTIVE           = 'Active'
PR_CANCELED         = 'Canceled'
PR_CLEARED          = 'Cleared'
PR_ACCEPTED         = 'Accepted'
PR_CREATED          = 'Created'
PR_COMPLETED        = 'Completed'
PR_DECLINED         = 'Declined'
PR_EXPIRED          = 'Expired'
PR_FAILED           = 'Failed'
PR_PAID             = 'Paid'
PR_PROCESSED        = 'Processed'
PR_PENDING          = 'Pending'
PR_REFUSED          = 'Refused'
PR_REVERSED         = 'Reversed'

PR_STATUS = [
    PR_ACCEPTED,PR_ACTIVE, PR_CANCELED, PR_CLEARED,
    PR_COMPLETED, PR_CREATED, PR_DECLINED, PR_EXPIRED,
    PR_FAILED, PR_PAID, PR_PENDING, PR_PROCESSED, 
    PR_REFUSED, PR_REVERSED
]


ORDER_SUBMITTED = 0
ORDER_PROCESSING = 1
ORDER_PAID = 2
ORDER_CANCELED = 3
ORDER_SHIPPED = 4
ORDER_DELIVERED = 5
ORDER_PICKED_UP = 6
ORDER_NOT_PICKED_UP = 7


ORDER_STATUS = (
    (ORDER_SUBMITTED, 'Submitted'),
    (ORDER_PROCESSING, 'Processing'),
    (ORDER_PAID, 'Paid'),
    (ORDER_CANCELED, 'Canceled'),
    (ORDER_SHIPPED, 'Shipped'),
    (ORDER_DELIVERED, 'Delivered'),
    (ORDER_PICKED_UP, 'Picked up'),
    (ORDER_NOT_PICKED_UP, 'Not picked  up'),
)

PAY_AT_DELIVERY = 0
PAY_AT_ORDER = 1

PAYMENT_OPTIONS = (
    (PAY_AT_DELIVERY, 'Pay at delivery'),
    (PAY_AT_ORDER, 'Pay at order'),
)


def get_order_status_name(order_status=None):
    key, value = utils.find_element_by_key_in_tuples(order_status, ORDER_STATUS)
    return key, value


def get_payment_option_name(option=None):
    key, value = utils.find_element_by_key_in_tuples(option, PAYMENT_OPTIONS)
    return key, value
