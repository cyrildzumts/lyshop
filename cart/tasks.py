from celery import task
from cart import cart_service
import logging


logger = logging.getLogger(__name__)



@task
def clean_coupons_tasks():
    logger.info("Starting clean_coupons_tasks")
    cart_service.coupons_cleanup()
    logger.info("Finished clean_coupons_tasks")