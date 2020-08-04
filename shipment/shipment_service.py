from django.db import IntegrityError
from shipment.models import Shipment, ShipmentStatusHistory, Shipment
from shipment import constants
from lyshop import conf, utils, settings
from orders.models import Order
from orders import commons
import logging
import uuid


logger = logging.getLogger(__name__)

ORDER_SHIPMENT_STATUS_MAPPING = {}
ORDER_SHIPMENT_STATUS_MAPPING[constants.WAITING] = commons.ORDER_READY_FOR_SHIPMENT
ORDER_SHIPMENT_STATUS_MAPPING[constants.PICKED_UP] = commons.ORDER_PICKED_UP
ORDER_SHIPMENT_STATUS_MAPPING[constants.PROCESSING] = commons.ORDER_PICKED_UP
ORDER_SHIPMENT_STATUS_MAPPING[constants.SHIPPED] = commons.ORDER_SHIPPED
ORDER_SHIPMENT_STATUS_MAPPING[constants.DELIVERED] = commons.ORDER_DELIVERED
ORDER_SHIPMENT_STATUS_MAPPING[constants.CLOSED] = commons.ORDER_CLOSED
ORDER_SHIPMENT_STATUS_MAPPING[constants.CUSTOMER_NOT_FOUND] = commons.ORDER_CUSTOMER_NOT_FOUND
ORDER_SHIPMENT_STATUS_MAPPING[constants.CUSTOMER_HAS_NOT_PAID] = commons.ORDER_CUSTOMER_HAS_NOT_PAID
ORDER_SHIPMENT_STATUS_MAPPING[constants.RETOURE] = commons.ORDER_RETOURE


def add_shipment(order):
    shippment = None
    if not isinstance(order, Order):
        logger.error("Type Error : order not of Order type")
        return shippment

    if Shipment.objects.filter(order=order).exists():
        logger.error("Add shipment Error : An shipment for this order already exists")
        return shippment
    data = {
        'shipment_number' : utils.generate_token_10(),
        'customer': order.user,
        'order' : order,
        'price' : order.shipping_price,
        'company': "LYSHOP"
    }
    try:
        shipment = Shipment.objects.create(**data)
    except IntegrityError as e:
        logger.error(f"IntegretyError on creating new Shipment for order \"{order.id}\"")
        logger.exception(e)
    
    if shipment:
        logger.info(f"Shipment created for order {order.pk}")
        ShipmentStatusHistory.objects.create(shipment=shipment,shipment_status=shipment.shipment_status, shipment_ref_id=shipment.id)
    else:
        logger.info(f"Shipment could not be created for order {order.pk}")
    return shipment



def get_next_order_status(shipment_status):
    shipment_key, shipment_value = utils.find_element_by_value_in_tuples(shipment_status, constants.SHIPMENT_STATUS)
    if shipment_key is None:
        raise LookupError("shipment_status not found")
    '''
    order_key, order_value = utils.find_element_by_value_in_tuples(order_status, commons.ORDER_STATUS)
    if order_key is None:
        raise LookupError("order_status not found")
    '''

    return ORDER_SHIPMENT_STATUS_MAPPING[shipment_status]
    


def update_order_status(order, shipment):
    if not isinstance(order, Order):
        msg = "Type Error : order not of Order type"
        logger.error(msg)
        raise TypeError(msg)
    if not isinstance(shipment, Shipment):
        msg = "Type Error : shipment not of Shipment type"
        logger.error(msg)
        raise TypeError(msg)
    if order.id != shipment.order.id:
        msg = "Illegal request. shipment does not belongs to the order"
        logger.error(msg)
        raise ValueError(msg)
    status = order.status
    try:
        status = get_next_order_status(shipment.shipment_status)
    except Exception as e:
        logger.error("Error on getting next order status")
        logger.exception(e)
    Order.objects.filter(id=order.id).update(status=status)


def find_order_shipment(order):
    if not isinstance(order, Order):
        logger.error("Type Error : order not of Order type")
        raise TypeError("Type Error : order argument not of type Order.")

    shipment = None
    try:
        shipment = Shipment.objects.get(order=order)
    except Shipment.DoesNotExist as e:
        pass
    return shipment

def shipment_for_order_exists(order):
    if not isinstance(order, Order):
        logger.error("Type Error : order not of Order type")
        raise TypeError("Type Error : order argument not of type Order.")
    return Shipment.objects.filter(order=order).exists()