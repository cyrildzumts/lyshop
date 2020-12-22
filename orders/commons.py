from django.utils.translation import gettext_lazy as _
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

# Unpaid orders submitted 'ORDER_PAID_DAY_DELAY' ago 
# must be cancelled
ORDER_PAID_DAY_DELAY = 3

PAYMENT_OPTION_FIELD        = "payment_option"
PAYMENT_METHOD_FIELD        = "payment_method"
SHIPPING_ADDRESS_FIELD      = "address"

KEY_REDIRECT_SUCCESS_URL    = 'redirect_success_url'
KEY_REDIRECT_FAILED_URL     = 'redirect_failed_url'
KEY_REDIRECT_PAYMENT_URL    = 'redirect_payment_url'



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
    (PAYMENT_PENDING, _('PENDING')),
    (PAYMENT_ACCEPTED, _('ACCEPTED')),
    (PAYMENT_REFUSED, _('REFUSED')),
    (PAYMENT_ACTIVE, _('ACTIVE')),
    (PAYMENT_CANCELED, _('CANCELED')),
    (PAYMENT_CLEARED, _('CLEARED')),
    (PAYMENT_CREATED, _('CREATED')),
    (PAYMENT_COMPLETED, _('COMPLETED')),
    (PAYMENT_EXPIRED, _('EXPIRED')),
    (PAYMENT_FAILED, _('FAILED')),
    (PAYMENT_PAID, _('PAID')),
    (PAYMENT_PROCESSED, _('PROCESSED')),
    (PAYMENT_REFUND, _('REFUND')),
    (PAYMENT_REFUNDED, _('REFUNDED')),
)

ORDER_STATUS = (
    (ORDER_SUBMITTED, _('SUBMITTED')),
    (ORDER_PROCESSING, _('PROCESSING')),
    (ORDER_PAID, _('PAID')),
    (ORDER_PAYMENT_FAILED, _('PAYMENT FAILED')),
    (ORDER_CANCELED, _('CANCELED')),
    (ORDER_SHIPPED, _('SHIPPED')),
    (ORDER_DELIVERED, _('DELIVERED')),
    (ORDER_PICKED_UP, _('PICKED UP')),
    (ORDER_CUSTOMER_NOT_FOUND, _('CUSTOMER NOT FOUND')),
    (ORDER_READY_FOR_SHIPMENT,_('READY FOR SHIPMENT')),
    (ORDER_REFUND, _('REFUND')),
    (ORDER_CUSTOMER_HAS_NOT_PAID, _('CUSTOMER HAS NOT PAID')),
    (ORDER_RETOURE, _('RETOURE')),
    (ORDER_CLOSED, _('CLOSED')),
    (ORDER_REFUNDED, _('REFUNDED')),
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
    (ORDER_PAYMENT_CASH, _("CASH")),
    (ORDER_PAYMENT_PAY, _("PAYMENT WITH PAY")),
    (ORDER_PAYMENT_MOBILE, _("MOBILE PAYMENT")),
)

PAYMENT_OPTIONS = (
    (PAY_AT_DELIVERY, _('PAY AT DELIVERY')),
    (PAY_AT_ORDER, _('PAY AT ORDER')),
    (PAY_BY_SMS, _('PAY BY SMS')),
    (PAY_WITH_PAY, _('PAY WITH PAY')),
    (PAY_BEFORE_DELIVERY, _('PAY BEFORE DELIVERY')),
)

ORDER_PAYMENT_OPTIONS = (
    (PAY_AT_DELIVERY, _('PAY AT DELIVERY')),
    (PAY_BEFORE_DELIVERY, _('PAY BEFORE DELIVERY')),
    (PAY_AT_ORDER, _('PAY AT ORDER')),
)


REFUND_PENDING = 0
REFUND_ACCEPTED = 1
REFUND_PAID = 2
REFUND_DECLINED = 3
REFUND_CANCELLED = 4

REFUND_DECLINED_UNSUFFICIENT_FUND = 0
REFUND_DECLINED_NOT_APPLICABLE = 1
REFUND_DECLINED_ARTICLE_USED = 2
REFUND_DECLINED_NOT_RETURNED_ON_TIME = 3

REFUND_STATUS = (
    (REFUND_PENDING, _('PENDING')),
    (REFUND_ACCEPTED, _('ACCEPTED')),
    (REFUND_PAID, _('REFUND')),
    (REFUND_DECLINED, _('DECLINED')),
    (REFUND_CANCELLED, _('CANCELLED')),
)

REFUND_DECLINED_REASON = (
    (REFUND_DECLINED_UNSUFFICIENT_FUND, _('UNSUFFICIENT FUND')),
    (REFUND_DECLINED_NOT_APPLICABLE, _('NOT APPLICABLE')),
    (REFUND_DECLINED_ARTICLE_USED, _('ARTICLE USED')),
    (REFUND_DECLINED_NOT_RETURNED_ON_TIME, _('ARTICLE NOT RETURNED ON TIME')),
)


def get_order_status_name(order_status=None):
    key, value = utils.find_element_by_key_in_tuples(order_status, ORDER_STATUS)
    return key, value


def get_payment_option_name(option=None):
    key, value = utils.find_element_by_key_in_tuples(option, ORDER_PAYMENT_OPTIONS)
    return key, value
