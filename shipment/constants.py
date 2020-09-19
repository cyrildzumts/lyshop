WAITING = 0
PICKED_UP = 1
SHIPPED = 2
DELIVERED = 3
PROCESSING = 4
RETOURE = 5
CUSTOMER_NOT_FOUND = 6
CUSTOMER_HAS_NOT_PAID = 7
CLOSED = 8

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