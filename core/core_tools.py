from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F, Q, Count, Sum
from django.core.mail import send_mail
from django.template.loader import get_template, render_to_string
from django.utils.translation import gettext_lazy as _
from django.forms import modelform_factory
from django.forms import formset_factory, modelformset_factory
from orders.models import Order, OrderItem
from lyshop import utils, settings
from xhtml2pdf import pisa
import logging
import datetime
import io

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



def generate_invoice(order, template_name=None, debug=False, output_name=None):
    template_name = template_name or "invoices/invoice.html"
    
    now = datetime.datetime.now()
    #start_date = now - datetime.timedelta(days=now.day-1, hours=now.hour, minutes=now.minute, seconds=now.second)
    #end_delta = datetime.timedelta(days=1,hours=-23, minutes=-59, seconds=-59)
    #end_date = datetime.datetime(now.year, now.month +1, 1) - end_delta
    #user_seller =  None
    if isinstance(order, Order):
        order_items = order.order_items.all()
    else:
        logger.warn("generate_invoice : no valid order")
        return

    
    context = {
        'SITE_NAME' : settings.SITE_NAME,
        'SITE_HOST': settings.SITE_HOST,
        'CONTACT_MAIL': settings.CONTACT_MAIL,
        'DATE': now,
        'orientation' : 'portrait',
        'FRAME_NUMBER' : 2,
        'page_size': 'letter portrait',
        'border': debug,
        'entry_list' : order_items,
        'TOTAL' : order.total,
        'COUNT': order.quantity,
        'CURRENCY': settings.CURRENCY,
        'INVOICE_TITLE' : f"Invoice-{order.order_ref_number}-{order.created_at}",
        'order': order
    }
    output_name = output_name or f"Invoice-{order.order_ref_number}-{order.created_at}.pdf"
    invoice_html = render_to_string(template_name, context)
    #invoce_pdf = open(output_name, 'w+b')
    invoice_file = io.BytesIO()
    pdf_status = pisa.CreatePDF(invoice_html, dest=invoice_file, debug=False)
    #invoice_file.close()
    if pdf_status.err:
        logger.error("error when creating the report pdf")
        return None
    else:
        logger.info("recharge report pdf created")
    return invoice_file



def generate_sold_products_reports(template_name, output_name, seller=None):
    template_name = template_name or "sold_products.html"
    now = datetime.datetime.now()
    start_date = now - datetime.timedelta(days=now.day-1, hours=now.hour, minutes=now.minute, seconds=now.second)
    end_delta = datetime.timedelta(days=1,hours=-23, minutes=-59, seconds=-59)
    end_date = datetime.datetime(now.year, now.month +1, 1) - end_delta
    user_seller =  None
    if isinstance(seller, str):
        try:
            user_seller = User.objects.get(username=seller)
            entry_list = OrderItem.objects.filter(product__product__sold_by=user_seller, order__is_paid=True, order__is_closed=True ,order__created_at__year=now.year, order__created_at__month=now.month)
        except User.DoesNotExist:
            logger.warn("report generator generate_sold_products_reports : no seller {seller} found")
            return
        #total = Recharge.objects.filter(created_at__year=now.year, created_at__month=now.month).aggregate(total=Sum('amount')).get('total') or 0
    elif isinstance(seller, User):
        user_seller = seller
        entry_list = OrderItem.objects.filter(product__product__sold_by=user_seller, order__is_paid=True, order__is_closed=True ,order__created_at__year=now.year, order__created_at__month=now.month)
    else:
        entry_list = OrderItem.objects.filter(order__is_paid=True, order__is_closed=True ,order__created_at__year=now.year, order__created_at__month=now.month)

    total_aggregrate = entry_list.aggregate(total=Sum('total_price'), total_promotion_price=Sum('total_promotion_price'), count=Sum('quantity'))
    total = total_aggregrate.get('total') or 0
    total_promotion_price = total_aggregrate.get('total_promotion_price') or 0
    count = total_aggregrate.get('count') or 0
    
    context = {
        'SITE_NAME' : settings.SITE_NAME,
        'SITE_HOST': settings.SITE_HOST,
        'CONTACT_MAIL': settings.CONTACT_MAIL,
        'DATE': now,
        'orientation' : 'portrait',
        'FRAME_NUMBER' : 2,
        'page_size': 'letter portrait',
        'border': '',
        'entry_list' : entry_list.order_by('-sold_at'),
        'TOTAL' : total,
        'TOTAL_PROMOTION_PRICE' : total_promotion_price,
        'COUNT': entry_list.count(),
        'CURRENCY': settings.CURRENCY,
        'REPORT_TITLE' : _('Sold Product Card Sumary'),
        'start_date': start_date,
        'end_date': end_date
    }
    report_html = render_to_string(template_name, context)
    report_pdf = open(output_name, 'w+b')
    pdf_status = pisa.CreatePDF(report_html, dest=report_pdf, debug=False)
    report_pdf.close()
    if pdf_status.err:
        logger.error("error when creating the report pdf")
    else:
        logger.info("sold voucher report pdf created")




def save_pdf_file(order, debug=True):
    byteio_file = generate_invoice(order, debug=debug)
    if not byteio_file:
        return
    output_name = f"Invoice-{order.order_ref_number}-{order.created_at}.pdf"
    with open(output_name, 'w+b') as f :
        f.write(byteio_file.getbuffer())