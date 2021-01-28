from celery import shared_task
from lyshop import settings
from orders import orders_service
import logging


logger = logging.getLogger(__name__)


@shared_task
def cancel_unpaid_orders_task():
    logger.info("Starting cancel_unpaid_orders_task")
    orders_service.clean_unpaid_orders()
    logger.info("Finished cancel_unpaid_orders_task")