
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from lyshop import settings
import logging


logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def send_welcome_mail(sender, instance, created, **kwargs):
    logger.debug("sending welcome mail ...")
    if created:
        logger.debug("new user created, sending welcome mail ...")
        email_context = {
            'template_name': settings.DJANGO_WELCOME_EMAIL_TEMPLATE,
            'title': 'Bienvenu chez LYSHOP',
            'recipient_email': instance.email,
            'context':{
                'SITE_NAME': settings.SITE_NAME,
                'SITE_HOST': settings.SITE_HOST,
                'FULL_NAME': instance.get_full_name()
            }
        }
        send_mail_task.apply_async(
            args=[email_context],
            queue=settings.CELERY_OUTGOING_MAIL_EXCHANGE,
            routing_key=settings.CELERY_OUTGOING_MAIL_ROUTING_KEY
        )
