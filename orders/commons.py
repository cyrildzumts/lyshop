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
ORDER_CUSTOMER_NOT_FOUND = 7
ORDER_READY_FOR_SHIPMENT = 8
ORDER_REFUND = 9
ORDER_CUSTOMER_HAS_NOT_PAID = 10
ORDER_RETOURE = 11
ORDER_CLOSED = 12


ORDER_STATUS = (
    ('SUBMITTED', ORDER_SUBMITTED),
    ('PROCESSING' ,ORDER_PROCESSING),
    ('PAID',ORDER_PAID),
    ('CANCELED', ORDER_CANCELED),
    ('SHIPPED', ORDER_SHIPPED),
    ('DELIVERED',ORDER_DELIVERED),
    ('PICKED UP', ORDER_PICKED_UP),
    ('CUSTOMER NOT FOUND', ORDER_CUSTOMER_NOT_FOUND),
    ('READY FOR SHIPMENT', ORDER_READY_FOR_SHIPMENT),
    ('REFUND', ORDER_REFUND),
    ('CUSTOMER HAS NOT PAID', ORDER_CUSTOMER_HAS_NOT_PAID),
    ('RETOURE', ORDER_RETOURE),
    ('CLOSED', ORDER_CLOSED),
)

PAY_AT_DELIVERY = 0
PAY_AT_ORDER = 1

PAYMENT_OPTIONS = (
    ('PAY AT DELIVERY', PAY_AT_DELIVERY),
    ('PAY AT ORDER', PAY_AT_ORDER),
)


def get_order_status_name(order_status=None):
    key, value = utils.find_element_by_value_in_tuples(order_status, ORDER_STATUS)
    return key, value


def get_payment_option_name(option=None):
    key, value = utils.find_element_by_value_in_tuples(option, PAYMENT_OPTIONS)
    return key, value
