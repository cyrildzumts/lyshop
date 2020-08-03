from django.db import IntegrityError
from shipment.models import Shipment, ShipmentStatusHistory, Shipment
from lyshop import conf, utils, settings
from orders.models import Order
import logging
import uuid


logger = logging.getLogger(__name__)

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
        shipment = Shipment.objects.create(data)
    except IntegrityError as e:
        logger.error(f"IntegretyError on creating new Shipment for order \"{order.id}\"")
        logger.exception(e)
    
    if shipment:
        logger.info(f"Shipment created for order {order.pk}")
        ShipmentStatusHistory.objects.create(shipment=shipment,shipment_status=shipment.shipment_status, shipment_ref_id=shipment.id)
    else:
        logger.info(f"Shipment could not be created for order {order.pk}")
    return shipment


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
    return Shipment.objects.filter(order=order).exists():