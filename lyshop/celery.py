import os
from kombu import Exchange, Queue
from lyshop import settings
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lyshop.settings')
app = Celery(settings.SITE_NAME)
app.config_from_object('django.conf:settings', namespace=settings.CELERY_NAMESPACE)
app.conf.task_queues = (
    Queue(settings.CELERY_DEFAULT_QUEUE, Exchange(settings.CELERY_DEFAULT_EXCHANGE), routing_key=settings.CELERY_DEFAULT_ROUTING_KEY),
    Queue(settings.CELERY_OUTGOING_MAIL_QUEUE, Exchange(settings.CELERY_OUTGOING_MAIL_EXCHANGE), routing_key=settings.CELERY_OUTGOING_MAIL_ROUTING_KEY),
    Queue(settings.CELERY_IDENTIFICATION_QUEUE, Exchange(settings.CELERY_IDENTIFICATION_EXCHANGE), routing_key=settings.CELERY_IDENTIFICATION_ROUTING_KEY),
)
app.conf.task_default_queue = settings.CELERY_DEFAULT_QUEUE
app.conf.task_default_exchange_type = settings.CELERY_DEFAULT_EXCHANGE_TYPE
app.conf.task_default_routing_key = settings.CELERY_DEFAULT_ROUTING_KEY
app.conf.beat_schedule = {
    'clean_unpaid_orders': {
        'task': 'orders.tasks.cancel_unpaid_orders_task',
        'schedule' : crontab(minute=0, hour='*/3')
    },
    'clean_coupons': {
        'task': 'cart.tasks.clean_coupons_tasks',
        'schedule' : crontab(minute=0, hour=0)
    }
}
app.autodiscover_tasks()