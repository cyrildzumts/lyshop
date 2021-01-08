from django.utils.translation import gettext_lazy as _

WAITING = 0
PICKED_UP = 1
SHIPPED = 2
DELIVERED = 3
PROCESSING = 4
RETOURE = 5
CUSTOMER_NOT_FOUND = 6
CUSTOMER_HAS_NOT_PAID = 7
CLOSED = 8

SHIP_STANDARD = 0
SHIP_EXPRESS  = 1
SHIP_IN_STORE = 2
SHIP_IN_STORE_POG = 3
SHIP_IN_STORE_LBV = 4

SHIP_MODE = (
    (SHIP_STANDARD, _('STANDARD SHIPMENT')),
    (SHIP_EXPRESS, _('EXPRESS SHIPMENT')),
    (SHIP_IN_STORE, _('IN STORE PICK UP')),
    (SHIP_IN_STORE_POG, _('IN STORE PICK UP(POG)')),
    (SHIP_IN_STORE_LBV, _('IN STORE PICK UP(LBV)')),
)

IN_STORE_PICK_MODE = [SHIP_IN_STORE, SHIP_IN_STORE_LBV, SHIP_IN_STORE_POG]

SHIPMENT_STATUS = (
    (WAITING, 'WAITING'),
    (PICKED_UP, 'PICKED UP'),
    (SHIPPED, 'SHIPPED'),
    (DELIVERED, 'DELIVERED'),
    (PROCESSING, 'PROCESSING'),
    (RETOURE, 'RETOURE'),
    (CUSTOMER_NOT_FOUND, 'CUSTOMER NOT FOUND'),
    (CUSTOMER_HAS_NOT_PAID,  'CUSTOMER CAN NOT PAY'),
    (CLOSED, 'CLOSED'),
)