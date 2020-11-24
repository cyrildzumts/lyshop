import timeit
import itertools
from lyshop import utils
import random

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
ORDER_PAYMENT_FAILED = 13
ORDER_REFUNDED = 14

ORDERED = [ORDER_SUBMITTED, ORDER_PROCESSING]
SOLD = [ORDER_PAID, ORDER_SHIPPED, ORDER_DELIVERED, ORDER_PICKED_UP, ORDER_READY_FOR_SHIPMENT]

PAYMENT_PENDING = 0
PAYMENT_ACCEPTED = 1
PAYMENT_REFUSED = 2
PAYMENT_ACTIVE = 3
PAYMENT_CANCELED = 4
PAYMENT_CLEARED = 5
PAYMENT_CREATED = 6
PAYMENT_COMPLETED = 7
PAYMENT_EXPIRED = 8
PAYMENT_FAILED  = 9
PAYMENT_PAID = 10
PAYMENT_PROCESSED = 11
PAYMENT_REFUND = 12
PAYMENT_REFUNDED = 13


PAYMENT_STATUS = (
    (PAYMENT_PENDING, 'PENDING'),
    (PAYMENT_ACCEPTED, 'ACCEPTED'),
    (PAYMENT_REFUSED, 'REFUSED'),
    (PAYMENT_ACTIVE, 'ACTIVE'),
    (PAYMENT_CANCELED, 'CANCELED'),
    (PAYMENT_CLEARED, 'CLEARED'),
    (PAYMENT_CREATED, 'CREATED'),
    (PAYMENT_COMPLETED, 'COMPLETED'),
    (PAYMENT_EXPIRED, 'EXPIRED'),
    (PAYMENT_FAILED, 'FAILED'),
    (PAYMENT_PAID, 'PAID'),
    (PAYMENT_PROCESSED, 'PROCESSED'),
    (PAYMENT_REFUND, 'REFUND'),
    (PAYMENT_REFUNDED, 'REFUNDED'),
)

ORDER_STATUS = (
    (ORDER_SUBMITTED, 'SUBMITTED'),
    (ORDER_PROCESSING, 'PROCESSING'),
    (ORDER_PAID, 'PAID'),
    (ORDER_PAYMENT_FAILED, 'PAYMENT FAILED'),
    (ORDER_CANCELED, 'CANCELED'),
    (ORDER_SHIPPED, 'SHIPPED'),
    (ORDER_DELIVERED, 'DELIVERED'),
    (ORDER_PICKED_UP, 'PICKED UP'),
    (ORDER_CUSTOMER_NOT_FOUND, 'CUSTOMER NOT FOUND'),
    (ORDER_READY_FOR_SHIPMENT,'READY FOR SHIPMENT'),
    (ORDER_REFUND, 'REFUND'),
    (ORDER_CUSTOMER_HAS_NOT_PAID, 'CUSTOMER HAS NOT PAID'),
    (ORDER_RETOURE, 'RETOURE'),
    (ORDER_CLOSED, 'CLOSED'),
    (ORDER_REFUNDED, 'REFUNDED'),
)

PAY_AT_DELIVERY = 0
PAY_AT_ORDER = 1
PAY_BY_SMS = 2
PAY_WITH_PAY = 3
PAY_BEFORE_DELIVERY = 4

ORDER_PAYMENT_CASH = 0
ORDER_PAYMENT_PAY = 1
ORDER_PAYMENT_MOBILE = 2

ORDER_PAYMENT_MODE = (
    (ORDER_PAYMENT_CASH, "CASH"),
    (ORDER_PAYMENT_PAY, "PAYMENT WITH PAY"),
    (ORDER_PAYMENT_MOBILE, "MOBILE PAYMENT"),
)

PAYMENT_OPTIONS = (
    (PAY_AT_DELIVERY, 'PAY AT DELIVERY'),
    (PAY_AT_ORDER, 'PAY AT ORDER'),
    (PAY_BY_SMS, 'PAY BY SMS'),
    (PAY_WITH_PAY, 'PAY WITH PAY'),
    (PAY_BEFORE_DELIVERY, 'PAY BEFORE DELIVERY'),
)

ORDER_PAYMENT_OPTIONS = (
    (PAY_AT_DELIVERY, 'PAY AT DELIVERY'),
    (PAY_BEFORE_DELIVERY, 'PAY BEFORE DELIVERY'),
    (PAY_AT_ORDER, 'PAY AT ORDER'),
)



def get_order_status_name(order_status=None):
    key, value = utils.find_element_by_key_in_tuples(order_status, ORDER_STATUS)
    return key, value


def get_payment_option_name(option=None):
    key, value = utils.find_element_by_key_in_tuples(option, ORDER_PAYMENT_OPTIONS)
    return key, value
