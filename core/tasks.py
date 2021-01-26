from django.core.mail import send_mail
from celery import shared_task
import django.template.loader as loader
from lyshop import settings
from orders import orders_service
import logging


logger = logging.getLogger(__name__)



@shared_task
def send_mail_task(email_context=None):
    
    # TODO : make sending email based on Django Template System.
    if email_context is not None:
        logger.debug("email_context available. Running send_mail now")
        template_name = email_context['template_name']
        #message = loader.render_to_string(template_name, {'email': email_context})
        html_message = loader.get_template(template_name=template_name).render({'email': email_context})
        send_mail(
            email_context['title'],
            None,
            settings.DEFAULT_FROM_EMAIL,
            [email_context['recipient_email']],
            html_message=html_message
        )
    else:
        logger.debug("email_context or template_name not available")


@shared_task
def cancel_unpaid_orders_task():
    logger.info("Starting cancel_unpaid_orders_task")
    orders_service.clean_unpaid_orders()
    logger.info("Finished cancel_unpaid_orders_task")