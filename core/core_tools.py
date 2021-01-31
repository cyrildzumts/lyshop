from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.forms import modelform_factory
from django.forms import formset_factory, modelformset_factory
from lyshop import utils
import logging

logger = logging.getLogger(__name__)

def create_instance(model, data):
    Form = modelform_factory(model, fields=model.FORM_FIELDS)
    form = Form(data)
    if form.is_valid():
        return form.save()
    else:
        logger.warn(f"Error on creating a new instance of {model}")
        logger.error(form.errors)
    return None


def update_instance(model, instance, data):
    Form = modelform_factory(model, fields=model.FORM_FIELDS)
    form = Form(data, instance=instance)
    if form.is_valid():
        return form.save()
    else:
        logger.warn(f"Error on updating an instance of {model}")
        logger.error(form.errors)
    return None


def delete_instance(model, data):
    logger.warn(f"Delete instance of {model} with data : {data}")
    return model.objects.filter(**data).delete()

def delete_instances(model, id_list):
    logger.warn(f"Delete instances of {model} with id in : {id_list}")
    return model.objects.filter(id__in=id_list).delete()


def instances_active_toggle(model, id_list, toggle=True):
    logger.warn(f"Updating active status for  instances of {model} with id in : {id_list}. new active status : {toggle}")
    return model.objects.filter(id__in=id_list).exclude(is_active=toggle).update(is_active=toggle)


def instances_sale_toggle(model, id_list, toggle=True):
    logger.warn(f"Updating active status for  instances of {model} with id in : {id_list}. new active status : {toggle}")
    return model.objects.filter(id__in=id_list).exclude(sale=toggle).update(sale=toggle)


def core_send_mail(recipient_list, subject, message):
    send_mail(subject, message, recipient_list)


def send_account_creation_confirmation(user):
    pass

def send_passwd_reset_confirmation(user):
    pass

def send_order_confirmation(order):
    pass

def send_order_cancel(order):
    pass

def send_payment_confirmation(order):
    pass

def send_shipment_confirmation(order):
    pass

def send_refund_confirmation(order):
    pass