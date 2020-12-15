from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied, SuspiciousOperation, ObjectDoesNotExist

from django.contrib.auth.models import User, Group, Permission
from django.http import Http404
from django.http import HttpResponseRedirect
from django.http import HttpResponseBadRequest
from django.http import HttpResponse
from django.urls import reverse, resolve
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseForbidden
from django.contrib import messages
from django.db.models import F, Q, Count, Sum
from django.utils import timezone
from django.forms import formset_factory, modelformset_factory
from dashboard.permissions import PermissionManager, get_view_permissions
from dashboard import Constants
from rest_framework.authtoken.models import Token
from lyshop import utils, settings, conf as GLOBAL_CONF
from dashboard.forms import (AccountForm, GroupFormCreation, PolicyForm, PolicyGroupForm, 
    PolicyGroupUpdateForm, PolicyGroupUpdateMembersForm, TokenForm, OrderSoldItemForm
)
from accounts.forms import AccountCreationForm, UserCreationForm
from accounts.account_services import AccountService
from catalog.models import (
    Product, Brand, Category, ProductAttribute, ProductVariant, Policy, PolicyGroup, PolicyMembership, ProductImage, ProductType, ProductTypeAttribute,
    Highlight
)
from orders.models import Order, OrderItem, PaymentRequest, OrderStatusHistory, PaymentMethod
from orders.forms import DashboardOrderUpdateForm, OrderItemUpdateForm, PaymentMethodForm
from orders import orders_service
from shipment import shipment_service
from catalog.forms import (BrandForm, ProductAttributeForm, 
    ProductForm, ProductVariantForm, ProductVariantUpdateForm, CategoryForm, ProductImageForm, AttributeForm, AddAttributeForm,
    DeleteAttributeForm, CategoriesDeleteForm, ProductTypeForm, ProductTypeAttributeForm, HighlightForm
)
from cart.models import Coupon
from cart.forms import CouponForm
from catalog import models
from catalog import catalog_service
from catalog import constants as Catalog_Constants
from core.filters import filters
from orders import commons as Order_Constants
from orders import orders_service
from vendors.models import SoldProduct, Balance, VendorPayment, BalanceHistory
from vendors import vendors_service
from addressbook.models import Address
from addressbook import addressbook_service, constants as Addressbook_Constants
from inventory import inventory_service
from dashboard import analytics
from itertools import islice
import json

import logging

logger = logging.getLogger(__name__)

# Create your views here.

#TODO : Add Required Login decoators

MAX_IMAGE_SIZE = 2097152


@login_required
def dashboard(request):
    template_name = "dashboard/dashboard.html"
    can_view_dashboard = PermissionManager.user_can_access_dashboard(request.user)
    page_title = _('Dashboard') + ' - ' + settings.SITE_NAME
    username = request.user.username
    context = {
            'name'          : username,
            'page_title'    : page_title,
            'is_allowed'     : can_view_dashboard
        }
    if not can_view_dashboard :
        logger.warning(f"Dashboard : PermissionDenied to user {username} for path {request.path}")
        raise PermissionDenied
    else : 
        
        context.update(get_view_permissions(request.user))

        logger.info(f"Authorized Access : User {username} has requested the Dashboard Page")

    return render(request, template_name, context)

@login_required
def category_create (request):
    template_name = 'dashboard/category_create.html'
    page_title = _('New Category')
    context = {
        'page_title': page_title
    }
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_add_category(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    if request.method == 'POST':
        category = inventory_service.create_category(utils.get_postdata(request))
        if category:
            messages.success(request,_('New Category created'))
            logger.info(f'[ OK ]New Category \"{category.name}\" added by user {request.user.username}' )
            return redirect('dashboard:categories')
        else:
            messages.error(request,_('Error when creating new category'))
            logger.error(f'[ NOT OK ] Error on adding New Category by user {request.user.username}. Errors : {form.errors}' )
    elif request.method == 'GET':
        form = CategoryForm()
    context['form'] = form
    context['category_list'] = models.Category.objects.filter(is_active=True)
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)
    



@login_required
def categories(request):
    template_name = 'dashboard/category_list.html'
    page_title = _('Category List')
    context = {
        'page_title': page_title
    }
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_view_category(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    queryset = models.Category.objects.all().order_by('-created_at')
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, GLOBAL_CONF.PAGINATED_BY)
    try:
        list_set = paginator.page(page)
    except PageNotAnInteger:
        list_set = paginator.page(1)
    except EmptyPage:
        list_set = None
    context['page_title'] = page_title
    context['category_list'] = list_set
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)

@login_required
def category_detail(request, category_uuid=None):
    template_name = 'dashboard/category_detail.html'
    page_title = _('Category')
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_view_category(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    context = {
        'page_title': page_title
    }

    category = get_object_or_404(models.Category, category_uuid=category_uuid)
    product_list = models.Product.objects.filter(category__category_uuid=category_uuid)
    context['page_title'] = page_title
    context['category'] = category
    context['product_list'] = product_list
    context['subcategory_list'] = Category.objects.filter(parent=category)
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)

@login_required
def category_update(request, category_uuid):
    template_name = 'dashboard/category_update.html'
    page_title = _('Edit Category')
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_change_category(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    category = get_object_or_404(models.Category, category_uuid=category_uuid)
    if request.method == 'POST':
        category , updated = inventory_service.update_category(utils.get_postdata(request), category)
        if updated:
            messages.success(request,_('Category updated'))
            logger.info(f'[ OK ] Category \"{category.name}\" updated by user {request.user.username}' )
            return redirect(category.get_dashboard_url())
        else:
            messages.error(request,_('Error when updating category'))
            logger.error(f'[ NOT OK ] Error on updating Category \"{category.name}\" added by user {request.user.username}' )

    form = CategoryForm(instance=category)
    context = {
        'page_title': page_title,
        'form' : form,
        'category':category,
        'category_list': Category.objects.exclude(id__in=[category.pk])
    }
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)

@login_required
def category_delete(request, category_uuid):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_delete_category(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    if request.method != "POST":
        raise SuspiciousOperation('Bad request. POST request expected but received a GET request')
    category = get_object_or_404(models.Category, category_uuid=category_uuid)
    Category.objects.filter(pk=category.pk).delete()
    return redirect('dashboard:categories')


@login_required
def categories_delete(request):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_delete_category(request.user):
        logger.warning(f"PermissionDenied to user \"{username}\" for path \"{request.path}\"")
        raise PermissionDenied
    if request.method != "POST":
        raise SuspiciousOperation('Bad request')
    postdata = utils.get_postdata(request)
    id_list = postdata.getlist('categories')

    if len(id_list):
        category_list = list(map(int, id_list))
        Category.objects.filter(id__in=category_list).delete()
        messages.success(request, f"Catergories \"{category_list}\" deleted")
        logger.info(f"Categories \"{category_list}\" deleted by user {username}")
        
    else:
        messages.error(request, f"Catergories  could not be deleted")
        logger.error(f"ID list invalid. Error : {id_list}")
    return redirect('dashboard:categories')


@login_required
def category_products(request, category_uuid=None):
    template_name = 'dashboard/category_product_list.html'
    username = request.user.username
    
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_view_category(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    category = get_object_or_404(models.Category, category_uuid=category_uuid)
    page_title = _('Category')
    context = {
        'page_title': page_title,
        'category' : category
    }

    queryset = models.Product.objects.filter(category__category_uuid=category_uuid)
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, GLOBAL_CONF.PAGINATED_BY)
    try:
        list_set = paginator.page(page)
    except PageNotAnInteger:
        list_set = paginator.page(1)
    except EmptyPage:
        list_set = None
    context['page_title'] = page_title
    context['product_list'] = list_set
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)




@login_required
def product_create(request):
    template_name = 'dashboard/product_create.html'
    page_title = _('New Product')
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_add_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    context = {
        'page_title': page_title,
    }
    
    username = request.user.username
    if request.method == 'POST':
        postdata = utils.get_postdata(request)
        product = inventory_service.create_product(postdata)
        if product:
            messages.success(request, _('New Product created'))
            logger.info(f'New product added by user \"{username}\"')
            return redirect('dashboard:products')
        else:
            messages.error(request, _('Product not created'))
            logger.error(f'Error on creating new product. Action requested by user \"{username}\"')

    form = ProductForm()
    context['form'] = form
    context['brand_list'] = models.Brand.objects.all()
    context['category_list'] = models.Category.objects.all()
    context['user_list'] = User.objects.all()
    context['product_type_list'] = ProductType.objects.all()
    context['GENDER'] = Catalog_Constants.GENDER
    context['DESCRIPTION_MAX_SIZE'] = Catalog_Constants.DESCRIPTION_MAX_SIZE
    context['SHORT_DESCRIPTION_MAX_SIZE'] = Catalog_Constants.SHORT_DESCRIPTION_MAX_SIZE
    context.update(get_view_permissions(request.user))
    return render(request, template_name, context)


@login_required
def orders(request):

    username = request.user.username
    can_access_dashboard = PermissionManager.user_can_access_dashboard(request.user)
    if not can_access_dashboard:
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    can_view_order = PermissionManager.user_can_view_order(request.user)
    if not can_view_order:
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    context = {}
    #queryset = Order.objects.all().order_by('-created_at')
    #queryset, selected_filters = filters.field_filter(Order, request.GET.copy())
    queryDict = request.GET.copy()
    field_filter = filters.Filter(Order, queryDict)
    queryset = field_filter.apply_filter()
    selected_filters = field_filter.selected_filters
    if queryset is None:
        queryset = Order.objects.order_by('-created_at')
    else:
        queryset = queryset.order_by('-created_at')
    template_name = "dashboard/order_list.html"
    page_title = _("Dashboard Orders") + " - " + settings.SITE_NAME
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, GLOBAL_CONF.PAGINATED_BY)
    try:
        list_set = paginator.page(page)
    except PageNotAnInteger:
        list_set = paginator.page(1)
    except EmptyPage:
        list_set = None
    context['page_title'] = page_title
    context['orders'] = list_set
    context['ORDER_STATUS'] = Order_Constants.ORDER_STATUS
    context['PAYMENT_OPTIONS'] = Order_Constants.PAYMENT_OPTIONS
    context['SELECTED_FILTERS'] = selected_filters
    context['FILTER_CONFIG'] = Order.FILTER_CONFIG
    context.update(get_view_permissions(request.user))
    context['can_delete_order'] = PermissionManager.user_can_delete_order(request.user)
    context['can_update_order'] = PermissionManager.user_can_change_order(request.user)
    return render(request,template_name, context)


@login_required
def order_detail(request, order_uuid=None):
    template_name = 'dashboard/order_detail.html'
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_view_order(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    page_title = _('Order Detail')
    

    order = get_object_or_404(Order, order_uuid=order_uuid)
    orderItems = OrderItem.objects.filter(order=order)
    context = {
        'page_title': page_title,
        'order': order,
        'shipment': shipment_service.find_order_shipment(order),
        'orderItems': orderItems,
        'ORDER_STATUS' : Order_Constants.ORDER_STATUS,
        'PAYMENT_OPTIONS': Order_Constants.PAYMENT_OPTIONS,
        'order_is_cancelable' :  orders_service.is_cancelable(order),
        'order_can_be_shipped' :  orders_service.can_be_shipped(order)
    }
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)

@login_required
def order_cancel(request, order_uuid):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_view_order(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_change_order(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    order = get_object_or_404(Order,user=request.user, order_uuid=order_uuid)
        
    if orders_service.is_cancelable(order):
        orders_service.cancel_order(order, request.user)
        OrderStatusHistory.objects.create(order_status=commons.ORDER_CANCELED, order=order, order_ref_id=order.id, changed_by=request.user)
        messages.success(request, "Your order has been canceled")
        logger.info(f"Order {order.id} canceled by user {request.user.username}")
    else:
        messages.error(request, "Error. Your order can no more be canceled")
        
    return redirect('dashboard:order-detail', order_uuid=order_uuid)


@login_required
def orders_clean(request):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_view_order(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_change_order(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
        
    orders_service.clean_unpaid_orders()
    messages.success(request, "Unpaid Orders has been cancelled")
    logger.info(f"Unpaid Orders cancelled by user {request.user.username}")
    
        
    return redirect('dashboard:orders')


@login_required
def order_update(request, order_uuid=None):
    template_name = 'dashboard/order_update.html'
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_view_order(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_change_order(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    
    order = get_object_or_404(Order, order_uuid=order_uuid)
    page_title = _('Order Detail')

    if request.method == 'POST':
        postdata = utils.get_postdata(request)
        utils.show_dict_contents(postdata, "ORDER POSTDATA")
        form = DashboardOrderUpdateForm(postdata, instance=order)
        if form.is_valid():
            order = form.save()
            msg = f'Order {order.order_ref_number} updated'
            messages.success(request, msg)
            logger.info(msg)
            return redirect('dashboard:order-detail', order_uuid=order_uuid)
        else:
            msg = f'Order {order.order_ref_number} could not be updated'
            messages.error(request, msg)
            logger.info(msg)
            logger.error(form.errors.items())

    form = DashboardOrderUpdateForm(instance=order)
    context = {
        'page_title': page_title,
        'order': order,
        'shipment': shipment_service.find_order_shipment(order),
        'ORDER_STATUS' : Order_Constants.ORDER_STATUS,
        'PAYMENT_OPTIONS': Order_Constants.PAYMENT_OPTIONS,
        'order_can_be_shipped' :  orders_service.can_be_shipped(order),
        'form': form
    }
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)


@login_required
def order_item(request, order_uuid=None, item_uuid=None):
    template_name = 'dashboard/order_item.html'
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_view_order(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    page_title = _('Order Item')
    

    order = get_object_or_404(Order, order_uuid=order_uuid)
    item = get_object_or_404(OrderItem, item_uuid=item_uuid)
    context = {
        'page_title': page_title,
        'order': order,
        'item' : item,
        'shipment': shipment_service.find_order_shipment(order),
        'ORDER_STATUS' : Order_Constants.ORDER_STATUS,
        'PAYMENT_OPTIONS': Order_Constants.PAYMENT_OPTIONS,
        'order_is_cancelable' :  orders_service.is_cancelable(order),
        'order_can_be_shipped' :  orders_service.can_be_shipped(order)
    }
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)


@login_required
def order_item_update(request, order_uuid=None, item_uuid=None):
    template_name = 'dashboard/order_item_update.html'
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_view_order(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_change_order(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    
    order = get_object_or_404(Order, order_uuid=order_uuid)
    item = get_object_or_404(OrderItem, item_uuid=item_uuid)
    product_count = order.order_items.count()
    page_title = _('Order Item Update')

    if request.method == 'POST':
        postdata = utils.get_postdata(request)
        form = OrderItemUpdateForm(postdata,instance=item)
        if form.is_valid():
            form.save()
            msg = f'Order Item {item} updated'
            messages.success(request, msg)
            logger.info(msg)
            return redirect('dashboard:order-detail', order_uuid=order_uuid)
        else:
            msg = f'Order Item {item} could not be updated'
            messages.error(request, msg)
            logger.info(msg)
            logger.error(form.errors.items())

    context = {
        'page_title': page_title,
        'order': order,
        'item' : item,
        'shipment': shipment_service.find_order_shipment(order),
        'ORDER_STATUS' : Order_Constants.ORDER_STATUS,
        'PAYMENT_OPTIONS': Order_Constants.PAYMENT_OPTIONS,
        'order_can_be_shipped' :  orders_service.can_be_shipped(order),
        'form': OrderItemUpdateForm(instance=item)
    }
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)


##TODO
'''
@login_required
def order_update_items(request, order_uuid=None):
    template_name = 'dashboard/order_update_items.html'
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_view_order(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_change_order(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    
    order = get_object_or_404(Order, order_uuid=order_uuid)
    product_count = order.order_items.count()
    page_title = _('Order Items Update')
    OrderSoldItemFormSet = formset_factory(OrderSoldItemForm, extra=product_count, max_num=product_count)
    if request.method == 'POST':
        postdata = utils.get_postdata(request)
        formset = OrderSoldItemFormSet(postdata)
        if formset.is_valid():
            
            msg = f'Order {order.order_ref_number} updated'
            messages.success(request, msg)
            logger.info(msg)
            return redirect('dashboard:order-detail', order_uuid=order_uuid)
        else:
            msg = f'Order {order.order_ref_number} could not be updated'
            messages.error(request, msg)
            logger.info(msg)
            logger.error(form.errors.items())

    context = {
        'page_title': page_title,
        'order': order,
        'shipment': shipment_service.find_order_shipment(order),
        'ORDER_STATUS' : Order_Constants.ORDER_STATUS,
        'PAYMENT_OPTIONS': Order_Constants.PAYMENT_OPTIONS,
        'order_can_be_shipped' :  orders_service.can_be_shipped(order),
        'formset': OrderSoldItemFormSet()
    }
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)
'''

@login_required
def add_order_for_shipment(request, order_uuid=None):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_change_order(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
 
    order = get_object_or_404(Order, order_uuid=order_uuid)
    shipment = shipment_service.add_shipment(order)
    if shipment is not None:
        messages.success(request, 'Order add for shipment')
    else:
        messages.error(request, 'Order could not be added for shipment')
    return redirect('dashboard:order-detail', order_uuid=order_uuid)

@login_required
def order_delete(request, order_uuid=None):
    template_name = 'dashboard/order_detail.html'
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_view_order(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    page_title = _('Order Detail')
    

    order = get_object_or_404(Order, order_uuid=order_uuid)
    orderItems = OrderItem.objects.filter(order=order)
    context = {
        'page_title': page_title,
        'order': order,
        'orderItems': orderItems,
    }
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)


@login_required
def order_history(request, order_uuid):
    order = get_object_or_404(Order, order_uuid=order_uuid)
    queryset = OrderStatusHistory.objects.filter(order=order)
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, GLOBAL_CONF.PAGINATED_BY)
    try:
        list_set = paginator.page(page)
    except PageNotAnInteger:
        list_set = paginator.page(1)
    except EmptyPage:
        list_set = None
    context = {
        'page_title' : _('Order Histories'),
        'history_list':  list_set,
        'order' : order,
        'ORDER_STATUS' : Order_Constants.ORDER_STATUS,
        'PAYMENT_OPTIONS': Order_Constants.PAYMENT_OPTIONS,
    }
    template_name = 'dashboard/order_histories.html'
    return render(request, template_name, context)

@login_required
def order_history_detail(request, history_uuid):
    history = get_object_or_404(OrderStatusHistory, history_uuid=history_uuid)
    context = {
        'page_title' : _('Order History'),
        'history':  history,
        'ORDER_STATUS' : Order_Constants.ORDER_STATUS,
        'PAYMENT_OPTIONS': Order_Constants.PAYMENT_OPTIONS,
    }
    template_name = 'dashboard/order_history.html'
    return render(request, template_name, context)


@login_required
def add_products_highlight(request, highlight_uuid):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_add_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    form = None
    username = request.user.username
    highlight = get_object_or_404(Highlight, highlight_uuid=highlight_uuid)
    if request.method == 'POST':
        postdata = utils.get_postdata(request)
        form = AddAttributeForm(postdata)
        logger.info("Attribute formset valid checking")
        if form.is_valid():
            attributes = form.cleaned_data['attributes']
            variant.attributes.add(*attributes)
            messages.success(request, _('Attribute formset valid'))
            logger.info(f'New attributes added by user \"{username}\"')
            logger.info(attributes)
        else:
            messages.error(request, _('Attributes not added'))
            logger.error(f'Error on adding new product variant attributes. Action requested by user \"{username}\"')
            logger.error(form.errors)
            
    return redirect('dashboard:product-variant-detail', variant_uuid=variant_uuid)


@login_required
def highlight_add_products(request, highlight_uuid):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_delete_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if request.method != "POST":
        raise SuspiciousOperation('Bad request')

    highlight = get_object_or_404(Highlight, highlight_uuid=highlight_uuid)
    postdata = utils.get_postdata(request)
    id_list = postdata.getlist('products')

    if len(id_list):
        id_list = list(map(int, id_list))
        highlight.products.add(*id_list)
        messages.success(request, f"Products \"{id_list}\" added to highlight {highlight.display_name}")
        logger.info(f"Products \"{id_list}\" added to highlight {highlight.display_name} by user {username}")
        
    else:
        messages.error(request, f"ID list invalid. Error : {id_list}")
        logger.error(f"ID list invalid. Error : {id_list}")
    return redirect(highlight.get_absolute_url())

@login_required
def highlights(request):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_view_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    template_name = 'dashboard/highlight_list.html'
    page_title = _('Highlights')
    context = {}

    queryset = Highlight.objects.order_by('-created_at')

    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, GLOBAL_CONF.PAGINATED_BY)
    try:
        list_set = paginator.page(page)
    except PageNotAnInteger:
        list_set = paginator.page(1)
    except EmptyPage:
        list_set = None
    context['page_title'] = page_title
    context['highlight_list'] = list_set
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)


@login_required
def highlight_create(request):
    template_name = 'dashboard/highlight_create.html'
    page_title = _('New Highlight')
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_add_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    context = {
        'page_title': page_title,
    }
    form = None
    
    username = request.user.username
    if request.method == 'POST':
        postdata = utils.get_postdata(request)
        form = HighlightForm(postdata)
        if form.is_valid():
            highlight = form.save()
            messages.success(request, _('New Highlight created'))
            logger.info(f'New highlight added by user \"{username}\"')
            return redirect(highlight.get_absolute_url())
        else:
            messages.error(request, _('Highlight not created'))
            logger.error(f'Error on creating new highlight. Action requested by user \"{username}\"')
            logger.error(form.errors.items())
    else:
        form = ProductForm()
    context['form'] = form
    context['GENDER'] = Catalog_Constants.GENDER
    context['DESCRIPTION_MAX_SIZE'] = Catalog_Constants.DESCRIPTION_MAX_SIZE
    context.update(get_view_permissions(request.user))
    return render(request, template_name, context)


@login_required
def highlight_detail(request, highlight_uuid=None):
    template_name = 'dashboard/highlight_detail.html'
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_view_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    page_title = _('Highlight Detail')
    

    highlight = get_object_or_404(Highlight, highlight_uuid=highlight_uuid)
    context = {
        'page_title': page_title,
        'highlighted_products': highlight.products.all(),
        'products': Product.objects.filter(quantity__gt=0).exclude(pk__in=highlight.products.all()),
        'highlight': highlight
    }
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)


@login_required
def highlight_update(request, highlight_uuid=None):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_change_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    template_name = 'dashboard/highlight_update.html'
    page_title = _('Highlight Update')
    context = {
        'page_title': page_title,
    }
    form = None
    highlight = get_object_or_404(Highlight, highlight_uuid=highlight_uuid)
    if request.method == 'POST':
        postdata = utils.get_postdata(request)
        form = HighlightForm(postdata, instance=highlight)
        if form.is_valid():
            highlight = form.save()
            messages.success(request, _('Highlight updated'))
            logger.info(f'highlight {highlight.name} updated by user \"{username}\"')
            return redirect('dashboard:highlight-detail', highlight_uuid=highlight_uuid)
        else:
            messages.error(request, _('highlight not updated'))
            logger.error(f'Error on updating highlight. Action requested by user \"{username}\"')
            logger.error(form.errors)
    else:
        form = HighlightForm(instance=highlight)
    context['form'] = form
    context['highlight'] = highlight
    context['products'] = highlight.products.all()
    context['GENDER'] = Catalog_Constants.GENDER
    context['DESCRIPTION_MAX_SIZE'] = Catalog_Constants.DESCRIPTION_MAX_SIZE

    context.update(get_view_permissions(request.user))
    return render(request, template_name, context)

@login_required
def highlight_delete(request, highlight_uuid=None):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_delete_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if request.method != "POST":
        raise SuspiciousOperation('Bad request')

    highlight = get_object_or_404(Highlight, highlight_uuid=highlight_uuid)
    Highlight.objects.filter(pk=highlight.pk).delete()
    logger.info(f'Highlight \"{highlight.name}\" deleted by user \"{request.user.username}\"')
    messages.success(request, _('Highlight deleted'))
    return redirect('dashboard:highlights')


@login_required
def highlight_clear(request, highlight_uuid=None):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_delete_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if request.method != "POST":
        raise SuspiciousOperation('Bad request')

    highlight = get_object_or_404(Highlight, highlight_uuid=highlight_uuid)
    highlight.products.clear()
    logger.info(f'Highlight \"{highlight.name}\" deleted by user \"{request.user.username}\"')
    messages.success(request, _('Highlight deleted'))
    return redirect('dashboard:highlight-detail', highlight_uuid=highlight_uuid)


@login_required
def highlights_delete(request):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_delete_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if request.method != "POST":
        raise SuspiciousOperation('Bad request')

    postdata = utils.get_postdata(request)
    id_list = postdata.getlist('highlights')

    if len(id_list):
        highlight_list = list(map(int, id_list))
        Highlight.objects.filter(id__in=highlight_list).delete()
        messages.success(request, f"Highlights \"{id_list}\" deleted")
        logger.info(f"Highlights \"{id_list}\" deleted by user {username}")
        
    else:
        messages.error(request, f"Highlight \"{id_list}\" could not be deleted")
        logger.error(f"ID list invalid. Error : {id_list}")
    return redirect('dashboard:highlights')


@login_required
def products(request):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_view_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    template_name = 'dashboard/product_list.html'
    page_title = _('Products')
    context = {
        'page_title': page_title,
    }

    #queryset = Product.objects.order_by('-created_at')
    queryDict = request.GET.copy()
    field_filter = filters.Filter(Product, queryDict)
    queryset = field_filter.apply_filter()
    selected_filters = field_filter.selected_filters
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, GLOBAL_CONF.PAGINATED_BY)
    try:
        list_set = paginator.page(page)
    except PageNotAnInteger:
        list_set = paginator.page(1)
    except EmptyPage:
        list_set = None
    context['page_title'] = page_title
    context['product_list'] = list_set
    context['SELECTED_FILTERS'] = selected_filters
    context['FILTER_CONFIG'] = Product.FILTER_CONFIG
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)

@login_required
def product_detail(request, product_uuid=None):
    template_name = 'dashboard/product_detail.html'
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_view_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    page_title = _('Product Detail')
    

    product = get_object_or_404(models.Product, product_uuid=product_uuid)
    images = ProductImage.objects.filter(product=product)
    variants = models.ProductVariant.objects.filter(product=product)
    context = {
        'page_title': page_title,
        'product': product,
        'variant_list': variants,
        'image_list': images
    }
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)

@login_required
def product_update(request, product_uuid=None):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_change_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    template_name = 'dashboard/product_update.html'
    page_title = _('Product Update')
    context = {
        'page_title': page_title,
    }
    form = None
    product = get_object_or_404(models.Product, product_uuid=product_uuid)
    username = request.user.username
    if request.method == 'POST':
        postdata = utils.get_postdata(request)
        form = ProductForm(postdata, instance=product)
        product, updated = inventory_service.update_product(postdata, product)
        if updated:
            messages.success(request, _('Product updated'))
            logger.info(f'product {product.name} updated by user \"{username}\"')
            return redirect('dashboard:product-detail', product_uuid=product_uuid)
        else:
            messages.error(request, _('Product not updated'))
            logger.error(f'Error on updating product. Action requested by user \"{username}\"')

    form = ProductForm(instance=product)
    context['form'] = form
    context['product'] = product
    context['brand_list'] = models.Brand.objects.all()
    context['category_list'] = models.Category.objects.all()
    context['user_list'] = User.objects.all()
    context['product_type_list'] = ProductType.objects.all()
    context['GENDER'] = Catalog_Constants.GENDER
    context['DESCRIPTION_MAX_SIZE'] = Catalog_Constants.DESCRIPTION_MAX_SIZE
    context['SHORT_DESCRIPTION_MAX_SIZE'] = Catalog_Constants.SHORT_DESCRIPTION_MAX_SIZE
    context.update(get_view_permissions(request.user))
    return render(request, template_name, context)

@login_required
def product_delete(request, product_uuid=None):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_delete_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if request.method != "POST":
        raise SuspiciousOperation('Bad request')

    product = get_object_or_404(models.Product, product_uuid=product_uuid)
    p_name = product.name
    Product.objects.filter(pk=product.pk).delete()
    logger.info(f'Product \"{p_name}\" deleted by user \"{request.user.username}\"')
    messages.success(request, _('Product deleted'))
    return redirect('dashboard:products')


@login_required
def products_delete(request):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_delete_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if request.method != "POST":
        raise SuspiciousOperation('Bad request')

    postdata = utils.get_postdata(request)
    id_list = postdata.getlist('products')

    if len(id_list):
        product_id_list = list(map(int, id_list))
        Product.objects.filter(id__in=product_id_list).delete()
        messages.success(request, f"Products \"{id_list}\" deleted")
        logger.info(f"Products \"{id_list}\" deleted by user {username}")
        
    else:
        messages.error(request, f"Products \"{id_list}\" could not be deleted")
        logger.error(f"ID list invalid. Error : {id_list}")
    return redirect('dashboard:products')


@login_required
def product_image_create(request, product_uuid=None):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_add_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    context = {}    
    template_name = "dashboard/product_image_create.html"
    page_title = "New Product Image" + " - " + settings.SITE_NAME
    context['page_title'] = page_title
    product = get_object_or_404(Product, product_uuid=product_uuid)
    forms = []
    forms_valid = []
    forms_errors = []
    if request.method == "POST":
        postdata = utils.get_postdata(request)
        files = request.FILES.copy()
        i = 1
        for k,v in files.items():
            forms.append(ProductImageForm(data={'name': f"{product.category.code}{product.brand.code}{product.id}-{i}", 'product': postdata.get('product'), 'product_variant': postdata.get('product_variant')},
            files={'image' : v}))
            i = i + 1
        logger.debug(files)
        logger.debug(f"Type of REQUEST.FILES : {type(files)}")
        #for f in files:
        #   logger.info(f"Image name : {f.name} -  Image size : {f.size} - Image type : {f.content_type}")
        #form = ProductImageForm(postdata, request.FILES)
        for f in forms:
            forms_valid.append(f.is_valid())
        if all(forms_valid):
            logger.info("all image forms are valid.")
            logger.info("Saving images ...")
            for f in forms:
                f.save()
            logger.info("[OK] Saving images done.")
            if request.is_ajax():
                return JsonResponse({'status': 'OK', 'message' : 'files uploaded'})
            return redirect('dashboard:product-detail', product_uuid=product_uuid)
        else:
            logger.error("at least one image form is not valid.")
            for i in range(len(forms_valid)):
                if not forms_valid[i]:
                    forms_errors.append(forms[i].errors.as_json())
            logger.error(f" Forms Errors  - Errors = {forms_errors}")
            if request.is_ajax():
                return JsonResponse({'status': 'NOT OK', 'message' : 'files not uploaded', 'errors' : forms_errors}, status=400)
        '''
        if form.is_valid():
            logger.info("submitted product image form is valide")
            logger.info("saving submitted product image form")
            form.save()
            logger.info("submitted form saved")
            if request.is_ajax():
                return JsonResponse({'status': 'OK', 'message' : 'files uploaded'})
            return redirect('dashboard:product-detail', product_uuid=product_uuid)
            
        else:
            logger.error("The form is not valide. Error : %s", form.non_field_errors)
            logger.error("The form is not valide. Error : %s", form.errors)
            if request.is_ajax():
                return JsonResponse({'status': 'NOT OK', 'message' : 'files not uploaded', 'errors' : form.errors.as_json()}, status=400)
        '''
    form = ProductImageForm()
    context['form'] = form
    context['product'] = product
    return render(request,template_name, context)

@login_required
def product_image_detail(request, image_uuid=None):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_view_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    context = {}
    p_image = get_object_or_404(ProductImage, image_uuid=image_uuid)

    template_name = "dashboard/product_image_detail.html"
    page_title = "Product Image" + " - " + settings.SITE_NAME
    context['page_title'] = page_title
    context['image'] = p_image
    return render(request,template_name, context)

def product_image_delete(request, image_uuid=None):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_delete_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    
    if request.method != "POST":
        raise SuspiciousOperation('Bad request')

    context = {}

    p_image = get_object_or_404(ProductImage, image_uuid=image_uuid)
    product = p_image.product
    p_image.delete_image_file()
    ProductImage.objects.filter(pk=p_image.pk).delete()
    return redirect(product.get_dashboard_url())

@login_required
def product_image_update(request, image_uuid=None):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_change_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    page_title = "Edit Product Image" + ' - ' + settings.SITE_NAME
    template_name = "dashboard/product_image_update.html"
    image = get_object_or_404(ProductImage, image_uuid=image_uuid)
    if request.method =="POST":
        form = ProductImageForm(request.POST, request.FILES, instance=image)
        if form.is_valid():
            logger.info("ProductImageForm is valid")
            form.save()
            return redirect(image.product.get_dashboard_url())
        else:
            logger.info("Edit image form is not valid. Errors : %s", form.errors)
            logger.info("Form clean data : %s", form.cleaned_data)
    elif request.method == 'GET':
        form = ProductImageForm(instance=image)
    context = {
            'page_title': page_title,
            'template_name': template_name,
            'image'  : image,
            'form': form
        }
    
    return render(request, template_name,context )

@login_required
def product_images(request, product_uuid):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_view_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    context = {}
    product = get_object_or_404(Product, product_uuid=product_uuid)
    queryset = ProductImage.objects.filter(product__product_uuid=product_uuid).order_by('-created_at')
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, GLOBAL_CONF.PAGINATED_BY)
    try:
        list_set = paginator.page(page)
    except PageNotAnInteger:
        list_set = paginator.page(1)
    except EmptyPage:
        list_set = None
    template_name = "dashboard/product_images_list.html"
    page_title = "Product Images" + " - " + settings.SITE_NAME
    context['page_title'] = page_title
    context['image_list'] = list_set
    context['product'] = product
    return render(request,template_name, context)

@login_required
def product_variant_create(request, product_uuid=None):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_add_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    template_name = 'dashboard/product_variant_create.html'
    page_title = _('New Product Variant')
    
    form = None
    username = request.user.username
    product = get_object_or_404(models.Product, product_uuid=product_uuid)
    attribute_formset = modelformset_factory(ProductAttribute, form=ProductAttributeForm, extra=4, max_num=5)
    if request.method == 'POST':
        postdata = utils.get_postdata(request)
        form = ProductVariantForm(postdata)
        #formset = attribute_formset(postdata)
        if form.is_valid():
            p_variant = form.save()
            #attributes = formset.save()
            #p_variant.attributes.add(*attributes)
            messages.success(request, _('New Product variant created'))
            logger.info(f'New product variant added by user \"{username}\"')
            return redirect('dashboard:product-detail', product_uuid=product_uuid)
        else:
            messages.error(request, _('Product variant not created'))
            logger.error(f'Error on creating new product variant. Action requested by user \"{username}\"')
            logger.error(form.errors)
    else:
        form = ProductVariantForm()
    context = {
        'page_title': page_title,
        'form' : form,
        'product' : product,
        'attribute_formset': attribute_formset(queryset=ProductAttribute.objects.none())
    }
    context['attribute_formset'] = attribute_formset
    context['ATTRIBUTE_TYPE'] = Catalog_Constants.ATTRIBUTE_TYPE
    context.update(get_view_permissions(request.user))
    return render(request, template_name, context)

@login_required
def create_product_variant(request, product_uuid=None):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_add_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    template_name = 'dashboard/create_product_variant.html'
    
    username = request.user.username
    product = get_object_or_404(models.Product, product_uuid=product_uuid)
    
    if request.method == 'POST':
        postdata = utils.get_postdata(request)
        variants = inventory_service.create_variant(product, postdata)
        if variants:
            count = len(variants)
            messages.success(request, _(f'New Product variants({count}) created'))
            logger.info(f'New product variants({count}) added by user \"{username}\"')
            return redirect('dashboard:product-detail', product_uuid=product_uuid)
        else:
            messages.error(request, _('Product variant not created'))
            logger.error(f'Error on creating new product variant. Action requested by user \"{username}\"')
    
    page_title = _('New Product Variant')
    form = ProductVariantForm()
    attribute_formset = modelformset_factory(ProductAttribute, form=ProductAttributeForm)
    context = {
        'page_title': page_title,
        'form' : form,
        'product' : product,
        'attribute_list' : inventory_service.get_product_type_attributes(product),
        'attribute_formset': attribute_formset(queryset=ProductAttribute.objects.none())
    }
    context['attribute_formset'] = attribute_formset
    context['ATTRIBUTE_TYPE'] = Catalog_Constants.ATTRIBUTE_TYPE
    context.update(get_view_permissions(request.user))
    return render(request, template_name, context)

@login_required
def product_variant_detail(request, variant_uuid=None):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_view_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    template_name = 'dashboard/product_variant_detail.html'
    page_title = _('Product Variant Detail')
    attr_types = [k for k,v in Catalog_Constants.ATTRIBUTE_TYPE]
    variant = get_object_or_404(models.ProductVariant, product_uuid=variant_uuid)
    product = variant.product
    attribute_formset = modelformset_factory(ProductAttribute, form=ProductAttributeForm, extra=4, max_num=5)
    attribute_list = variant.attributes.all()
    available_attribute_list = ProductAttribute.objects.exclude(id__in=attribute_list.values_list('id'))
    context = {
        'page_title': page_title,
        'product': product,
        'variant': variant,
        'attr_types': json.dumps(attr_types),
        'ATTRIBUTE_TYPE' : Catalog_Constants.ATTRIBUTE_TYPE,
        'attribute_list' : attribute_list,
        'available_attribute_list' : available_attribute_list,
        'attribute_formset': attribute_formset(queryset=ProductAttribute.objects.none())
    }
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)

@login_required
def product_variant_update(request, variant_uuid=None):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_change_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    template_name = 'dashboard/product_variant_update.html'
    page_title = _('Product Variant Update')
    
    form = None
    username = request.user.username
    variant = get_object_or_404(models.ProductVariant, product_uuid=variant_uuid)
    product = variant.product
    attribute_formset = modelformset_factory(ProductAttribute, form=ProductAttributeForm, extra=4, max_num=5)
    if request.method == 'POST':
        postdata = utils.get_postdata(request)
        form = ProductVariantUpdateForm(postdata, instance=variant)
        if form.is_valid():
            p_variant = form.save()
            messages.success(request, _('Product variant updated'))
            logger.info(f'Product variant updated by user \"{username}\"')
            return redirect('dashboard:product-variant-detail', variant_uuid=variant_uuid)
        else:
            messages.error(request, _('Product variant not created'))
            logger.error(f'Error on updating product variant. Action requested by user \"{username}\"')
            #logger.error(formset.errors)
    else:
        form = ProductVariantForm(instance=variant)
    context = {
        'page_title': page_title,
        'form' : form,
        'product' : product,
        'variant' : variant,
        'attributes': variant.attributes.all(),
        'attribute_formset': attribute_formset,
        'attribute_types': Catalog_Constants.ATTRIBUTE_TYPE
    }
    context.update(get_view_permissions(request.user))
    return render(request, template_name, context)

@login_required
def product_variant_delete(request, variant_uuid=None):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_delete_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if request.method != "POST":
        logger.warning(f"Delete request refused. User {request.user.username} trying to delete a product variant {variant_uuid} in non POST request")
        logger.warning(f"request method used for the Delete : \"{request.method}\"")
        raise SuspiciousOperation('Bad request')

    product_variant = get_object_or_404(models.ProductVariant, product_uuid=variant_uuid)
    product = product_variant.product
    ProductVariant.objects.filter(pk=product_variant.pk).delete()
    logger.info(f'Product Variant \"{product_variant.display_name}\" deleted by user \"{request.user.username}\"')
    messages.success(request, _('Product variant deleted'))
    return redirect(product.get_dashboard_url())



@login_required
def sold_product_list(request):
    username = request.user.username
    
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_delete_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    template_name = 'dashboard/sold_product_list.html'
    page_title = _('Products')
    context = {
        'page_title': page_title,
    }

    queryset = SoldProduct.objects.all().order_by('-created_at')
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, GLOBAL_CONF.PAGINATED_BY)
    try:
        list_set = paginator.page(page)
    except PageNotAnInteger:
        list_set = paginator.page(1)
    except EmptyPage:
        list_set = None
    context['page_title'] = page_title
    context['product_list'] = list_set
    context.update(get_view_permissions(request.user))

    return render(request,template_name, context)


@login_required
def sold_product_detail(request, product_uuid=None):
    template_name = 'dashboard/sold_product_detail.html'
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_delete_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    page_title = _('Product Detail')
    

    sold_product = get_object_or_404(SoldProduct, product_uuid=product_uuid)
    images = ProductImage.objects.filter(product=sold_product.product.product)
    context = {
        'page_title': page_title,
        'sold_product': sold_product,
        'product' : sold_product.product.product,
        'variant' : sold_product.product,
        'attribute_list': sold_product.product.attributes.all(),
        'image_list': images
    }
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)



@login_required
def sold_product_delete(request, product_uuid=None):
    username = request.user.username
    
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_delete_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if request.method != "POST":
        raise SuspiciousOperation('Bad request')

    product = get_object_or_404(SoldProduct, product_uuid=product_uuid)
    p_name = product.product.name
    SoldProduct.objects.filter(pk=product.pk).delete()
    logger.info(f'SoldProduct \"{p_name}\" deleted by user \"{request.user.username}\"')
    messages.success(request, _('SoldProduct deleted'))
    return redirect('dashboard:sold-products')



@login_required
def sold_products_delete(request):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_delete_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied


    if request.method != "POST":
        raise SuspiciousOperation('Bad request. Expected POST request but received a GET')
    
    postdata = utils.get_postdata(request)
    id_list = postdata.getlist('products')

    if len(id_list):
        product_list = list(map(int, id_list))
        SoldProduct.objects.filter(id__in=product_list).delete()
        messages.success(request, f"SoldProduct \"{product_list}\" deleted")
        logger.info(f"SoldProduct\"{product_list}\" deleted by user {username}")
        
    else:
        messages.error(request, f"SoldProduct could not be deleted")
        logger.error(f"ID list invalid. Error : {id_list}")
    return redirect('dashboard:sold-products')



@login_required
def add_attributes(request, variant_uuid):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_add_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    form = None
    username = request.user.username
    variant = get_object_or_404(ProductVariant, product_uuid=variant_uuid)
    if request.method == 'POST':
        postdata = utils.get_postdata(request)
        form = AddAttributeForm(postdata)
        logger.info("Attribute formset valid checking")
        if form.is_valid():
            attributes = form.cleaned_data['attributes']
            variant.attributes.add(*attributes)
            messages.success(request, _('Attribute formset valid'))
            logger.info(f'New attributes added by user \"{username}\"')
            logger.info(attributes)
        else:
            messages.error(request, _('Attributes not added'))
            logger.error(f'Error on adding new product variant attributes. Action requested by user \"{username}\"')
            logger.error(form.errors)
            
    return redirect('dashboard:product-variant-detail', variant_uuid=variant_uuid)


@login_required
def remove_attributes(request, variant_uuid):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_delete_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    form = None
    username = request.user.username
    variant = get_object_or_404(ProductVariant, product_uuid=variant_uuid)
    if request.method == 'POST':
        postdata = utils.get_postdata(request)
        form = AddAttributeForm(postdata)
        if form.is_valid():
            attributes = form.cleaned_data['attributes']
            variant.attributes.remove(*attributes)
            messages.success(request, _('Attribute removed'))
            logger.info(f'attributes removed from product {variant.name} added by user \"{username}\"')
        else:
            messages.error(request, _('Attributes not removed'))
            logger.error(f'Error on removing attributes from product variant {variant.name}. Action requested by user \"{username}\"')
            logger.error(form.errors)
            
    return redirect('dashboard:product-variant-detail', variant_uuid=variant_uuid)




@login_required
def attribute_create(request, variant_uuid):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_add_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    template_name = 'dashboard/attribute_create.html'
    page_title = _('New Attribute')

    variant = get_object_or_404(ProductVariant, product_uuid=variant_uuid)
    attribute_formset = modelformset_factory(ProductAttribute, form=ProductAttributeForm)
    if request.method == 'POST':
        postdata = utils.get_postdata(request)
        formset = attribute_formset(postdata)
        logger.info("Attribute formset valid checking")
        if formset.is_valid():
            logger.info("Attribute formset valid")
            attributes = formset.save()
            variant.attributes.add(*attributes)
            messages.success(request, _('Attribute formset valid'))
            logger.info(f'New attributes added by user \"{username}\"')
            return redirect('dashboard:product-variant-detail', variant_uuid=variant_uuid)
        else:
            messages.error(request, _('Product variant not created'))
            logger.error(f'Error on creating new product variant. Action requested by user \"{username}\"')
            logger.error(formset.errors)
            return redirect('dashboard:product-variant-detail', variant_uuid=variant_uuid)

    context = {
        'page_title': page_title,
        'formset' : attribute_formset(),
        'variant' : variant
    }
    context['attribute_formset'] = attribute_formset
    context['attribute_types'] = Catalog_Constants.ATTRIBUTE_TYPE
    context['ATTRIBUTE_TYPE'] = Catalog_Constants.ATTRIBUTE_TYPE
    context.update(get_view_permissions(request.user))
    return render(request, template_name, context)


@login_required
def bulk_attributes_create(request):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_delete_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    form = None
    username = request.user.username
    if request.method == 'POST':
        postdata = utils.get_postdata(request)
        attrs, created = inventory_service.bulk_create_attributes(postdata)
        if created:
            messages.success(request, _('Attributes created'))
            logger.info(f'attributes created iin bluk by user \"{username}\"')
        else:
            messages.error(request, _('Attributes not created'))
            logger.error(f'Error on bulk creating attributes. Action requested by user \"{username}\"')
            logger.error(form.errors)
            
    return redirect('dashboard:attributes')

@login_required
def attributes_create(request):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_add_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    template_name = 'dashboard/attributes_create.html'
    page_title = _('New Attributes')
    
    attribute_formset = modelformset_factory(ProductAttribute, form=ProductAttributeForm)
    if request.method == 'POST':
        postdata = utils.get_postdata(request)
        formset = attribute_formset(postdata)
        logger.info("Attribute formset valid checking")
        if formset.is_valid():
            logger.info("Attribute formset valid")
            attrs = formset.save()
            messages.success(request, _('Attribute formset valid'))
            logger.info(f'New attributes added by user \"{username}\"')
            logger.info(f"attrs type : {type(attrs)}")
            return redirect('dashboard:attributes')
        else:
            messages.error(request, _('Product variant not created'))
            logger.error(f'Error on creating new attribute. Action requested by user \"{username}\"')
            logger.error(formset.errors)
            return redirect('dashboard:attributes-create')

    context = {
        'page_title': page_title,
        'formset' : attribute_formset(),
    }
    context['attribute_formset'] = attribute_formset
    context['ATTRIBUTE_TYPE'] = Catalog_Constants.ATTRIBUTE_TYPE
    context.update(get_view_permissions(request.user))
    return render(request, template_name, context)

@login_required
def attribute_delete(request, attribute_uuid=None):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_delete_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    if request.method != "POST":
        raise SuspiciousOperation('Bad request')

    attribute = get_object_or_404(ProductAttribute, attribute_uuid=attribute_uuid)
    ProductAttribute.objects.filter(id=attribute.id).delete()
    logger.info(f'Attribute \"{attribute.name}\" - value \"{attribute.value}\"  removed  by user \"{request.user.username}\"')
    messages.success(request, _('Product deleted'))
    return redirect('dashboard:attributes' )


@login_required
def delete_attributes(request):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_delete_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    form = None
    username = request.user.username
    if request.method == 'POST':
        postdata = utils.get_postdata(request)
        form = DeleteAttributeForm(postdata)
        if form.is_valid():
            attributes = form.cleaned_data['attributes']
            ProductAttribute.objects.filter(id__in=attributes).delete()
            messages.success(request, _('Attribute removed'))
            logger.info(f'attributes {attributes} removed  by user \"{username}\"')
        else:
            messages.error(request, _('Attributes not removed'))
            logger.error(f'Error on removing attributes. Action requested by user \"{username}\"')
            logger.error(form.errors)
            
    return redirect('dashboard:attributes')


@login_required
def attribute_detail(request, attribute_uuid):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_view_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    template_name = 'dashboard/attribute_detail.html'
    page_title = _('Attribute')
    
    attribute = get_object_or_404(ProductAttribute, attribute_uuid=attribute_uuid)
    context = {
        'page_title': page_title,
        'attribute' : attribute,
        'product_list': attribute.products.all(),
        'ATTRIBUTE_TYPE': Catalog_Constants.ATTRIBUTE_TYPE
    }
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)

@login_required
def attribute_update(request, attribute_uuid=None):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_change_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    
    form = None
    username = request.user.username
    attribute = get_object_or_404(ProductAttribute, attribute_uuid=attribute_uuid)
    if request.method == 'POST':
        postdata = utils.get_postdata(request)
        form = ProductAttributeForm(postdata, instance=attribute)
        if form.is_valid():
            attribute = form.save()
            messages.success(request, _('Attribute updated'))
            logger.info(f'Attribute updated by user \"{username}\"')
            return redirect(attribute.get_dashboard_url())
        else:
            messages.error(request, _('Attribute not updated'))
            logger.error(f'Error on updated Attribute. Action requested by user \"{username}\"')
            logger.error(f"Errors : {form.errors}")

    return redirect(attribute.get_dashboard_url())


@login_required
def attributes(request):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_view_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    template_name = 'dashboard/attribute_list.html'
    page_title = _('Product Attributes')


    queryset = ProductAttribute.objects.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, GLOBAL_CONF.PAGINATED_BY)
    try:
        list_set = paginator.page(page)
    except PageNotAnInteger:
        list_set = paginator.page(1)
    except EmptyPage:
        list_set = None
    context = {
        'page_title': page_title,
        'attribute_list': list_set,
        'has_default_not_set' : ProductAttribute.objects.filter(name__in=Catalog_Constants.DEFAULT_PRIMARY_ATTRIBUTES, is_primary=False).exists()
    }
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)

@login_required
def update_primary_attributes(request):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_change_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    catalog_service.update_default_attributes_primary()
            
    return redirect('dashboard:attributes')

@login_required
def brands(request):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_view_brand(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    template_name = 'dashboard/brand_list.html'
    page_title = _('Brands')
    if request.method != 'GET':
        return HttpResponseBadRequest('Bad request')

    queryset = models.Brand.objects.all().order_by('-created_at')
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, GLOBAL_CONF.PAGINATED_BY)
    try:
        list_set = paginator.page(page)
    except PageNotAnInteger:
        list_set = paginator.page(1)
    except EmptyPage:
        list_set = None
    context = {
        'page_title': page_title,
        'brand_list': list_set
    }
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)

@login_required
def brand_create(request):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_add_brand(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    template_name = 'dashboard/brand_create.html'
    page_title = _('New Brand')
    
    form = None
    username = request.user.username
    if request.method == 'POST':
        postdata = utils.get_postdata(request)
        form = BrandForm(postdata)
        if form.is_valid():
            brand = form.save()
            messages.success(request, _('New Brand created'))
            logger.info(f'New Brand added by user \"{username}\"')
            return redirect('dashboard:brands')
        else:
            messages.error(request, _('Brand not created'))
            logger.error(f'Error on creating new Brand. Action requested by user \"{username}\"')
    else:
        form = BrandForm()
    context = {
        'page_title': page_title,
        'form' : form
    }
    context.update(get_view_permissions(request.user))
    return render(request, template_name, context)

@login_required
def brand_detail(request, brand_uuid=None):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_view_brand(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    template_name = 'dashboard/brand_detail.html'
    page_title = _('Brand Detail')
    
    if request.method != "GET":
        raise SuspiciousOperation('Bad request')

    brand = get_object_or_404(models.Brand, brand_uuid=brand_uuid)
    product_list = Product.objects.filter(brand=brand)
    context = {
        'page_title': page_title,
        'product_list': product_list,
        'brand': brand
    }
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)

@login_required
def brand_update(request, brand_uuid=None):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_change_brand(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    template_name = 'dashboard/brand_update.html'
    page_title = _('Brand Update')
    
    form = None
    username = request.user.username
    brand = get_object_or_404(models.Brand, brand_uuid=brand_uuid)
    if request.method == 'POST':
        postdata = utils.get_postdata(request)
        form = BrandForm(postdata, instance=brand)
        if form.is_valid():
            brand = form.save()
            messages.success(request, _('Brand updated'))
            logger.info(f'Brand updated by user \"{username}\"')
            return redirect('dashboard:brand-detail', brand_uuid=brand_uuid)
        else:
            messages.error(request, _('Brand not updated'))
            logger.error(f'Error on updated Brand. Action requested by user \"{username}\"')
    else:
        form = BrandForm(instance=brand)
    context = {
        'page_title': page_title,
        'form' : form,
        'brand': brand
    }
    context.update(get_view_permissions(request.user))
    return render(request, template_name, context)


@login_required
def brand_delete(request, brand_uuid=None):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_delete_brand(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if request.method != "POST":
        raise SuspiciousOperation('Bad request')

    brand = get_object_or_404(models.Brand, brand_uuid=brand_uuid)
    brand_name = brand.name
    brand.delete()
    logger.info(f'Brand \"{brand_name}\" deleted by user \"{request.user.username}\"')
    messages.success(request, _('Brand deleted'))
    return redirect('dashboard:brands')


@login_required
def brands_delete(request):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_delete_brand(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if request.method != "POST":
        raise SuspiciousOperation('Bad request. Expected POST request but received a GET')
    
    postdata = utils.get_postdata(request)
    id_list = postdata.getlist('brands')

    if len(id_list):
        brand_list = list(map(int, id_list))
        Brand.objects.filter(id__in=brand_list).delete()
        messages.success(request, f"Brands \"{brand_list}\" deleted")
        logger.info(f"Brands\"{brand_list}\" deleted by user {username}")
        
    else:
        messages.error(request, f"Brands could not be deleted")
        logger.error(f"ID list invalid. Error : {id_list}")
    return redirect('dashboard:brands')


@login_required
def brand_products(request, brand_uuid=None):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_view_brand(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    template_name = 'dashboard/brand_product_list.html'
    page_title = _('Brand Products')
    
    if request.method != 'GET':
        return HttpResponseBadRequest('Bad request')

    brand = get_object_or_404(models.Brand, brand_uuid=brand_uuid)
    queryset = models.Product.objects.filter(brand=brand)
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, GLOBAL_CONF.PAGINATED_BY)
    try:
        list_set = paginator.page(page)
    except PageNotAnInteger:
        list_set = paginator.page(1)
    except EmptyPage:
        list_set = None
    context = {
        'page_title': page_title,
        'product_list': list_set,
        'brand': brand
    }
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)


@login_required
def brand_product_detail(request, brand_uuid=None, product_uuid=None):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_view_brand(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    template_name = 'dashboard/brand_product_detail.html'
    page_title = _('Product Detail')
    

    product = get_object_or_404(models.Product, Q(brand__brand_uuid=brand_uuid), product_uuid=product_uuid,)
    context = {
        'page_title': page_title,
        'product': product
    }
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)


@login_required
def tokens(request):
    username = request.user.username
    can_access_dashboard = PermissionManager.user_can_access_dashboard(request.user)
    if not can_access_dashboard:
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    can_view_user = PermissionManager.user_can_view_user(request.user)
    if not can_view_user:
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    context = {}
    queryset = Token.objects.all()
    template_name = "dashboard/token_list.html"
    page_title = _("Dashboard Users Tokens") + " - " + settings.SITE_NAME
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, GLOBAL_CONF.PAGINATED_BY)
    try:
        list_set = paginator.page(page)
    except PageNotAnInteger:
        list_set = paginator.page(1)
    except EmptyPage:
        list_set = None
    context['page_title'] = page_title
    context['token_list'] = list_set
    context.update(get_view_permissions(request.user))
    context['can_delete'] = PermissionManager.user_can_delete_user(request.user)
    return render(request,template_name, context)

@login_required
def generate_token(request):
    username = request.user.username
    can_view_dashboard = PermissionManager.user_can_access_dashboard(request.user)
    if not can_view_dashboard :
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    can_generate_token = PermissionManager.user_can_generate_token(request.user)
    if not can_generate_token:
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    template_name = "dashboard/token_generate.html"
    context = {
        'page_title' :_('User Token Generation') + ' - ' + settings.SITE_NAME,
        'can_generate_token' : can_generate_token,
    }
    if request.method == 'POST':
            form = TokenForm(utils.get_postdata(request))
            if form.is_valid():
                user_id = form.cleaned_data.get('user')
                user = User.objects.get(pk=user_id)
                t = Token.objects.get_or_create(user=user)
                context['generated_token'] = t
                logger.info("user \"%s\" create a token for user \"%s\"", request.user.username, user.username )
                messages.add_message(request, messages.SUCCESS, _('Token successfully generated for user {}'.format(username)) )
                return redirect('dashboard:home')
            else :
                logger.error("TokenForm is invalid : %s\n%s", form.errors, form.non_field_errors)
                messages.add_message(request, messages.ERROR, _('The submitted form is not valid') )
    else :
            context['form'] = TokenForm()
            context.update(get_view_permissions(request.user))
        

    return render(request, template_name, context)


@login_required
def reports(request):
    username = request.user.username
    can_access_dashboard = PermissionManager.user_can_access_dashboard(request.user)
    if not can_access_dashboard:
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    can_view_order = PermissionManager.user_can_view_order(request.user)
    if not can_view_order:
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    context = {}
    qs_orders = Order.objects.all()
    currents_orders = analytics.get_orders()
    qs_users = User.objects.all()
    qs_products = ProductVariant.objects.filter(is_active=True)
    qs_total_product = ProductVariant.objects.aggregate(product_count=Sum('quantity'))
    template_name = "dashboard/reports.html"
    page_title = _("Dashboard Reports") + " - " + settings.SITE_NAME
    
    context['page_title'] = page_title
    context['recent_orders'] = qs_orders[:Constants.MAX_RECENT]
    context['orders'] = qs_orders
    context['current_orders'] = currents_orders
    context['users'] = qs_users
    context['products'] = qs_products
    context['product_count'] = qs_total_product['product_count']
    context['report'] = json.dumps(analytics.report_orders())
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)
        
@login_required
def users(request):
    username = request.user.username
    can_access_dashboard = PermissionManager.user_can_access_dashboard(request.user)
    if not can_access_dashboard:
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    can_view_user = PermissionManager.user_can_view_user(request.user)
    if not can_view_user:
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    context = {}
    queryset = User.objects.all()
    template_name = "dashboard/user_list.html"
    page_title = _("Dashboard Users") + " - " + settings.SITE_NAME
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, GLOBAL_CONF.PAGINATED_BY)
    try:
        list_set = paginator.page(page)
    except PageNotAnInteger:
        list_set = paginator.page(1)
    except EmptyPage:
        list_set = None
    context['page_title'] = page_title
    context['users'] = list_set
    context.update(get_view_permissions(request.user))
    context['can_delete_user'] = PermissionManager.user_can_delete_user(request.user)
    context['can_add_user'] = PermissionManager.user_can_add_user(request.user)
    context['can_update_user'] = PermissionManager.user_can_change_user(request.user)
    return render(request,template_name, context)

@login_required
def user_details(request, pk=None):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    if not PermissionManager.user_can_view_user(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    context = {}
    #queryset = User.objects.select_related('account')
    user = get_object_or_404(User, pk=pk)
    product_list = Product.objects.filter(sold_by=user, quantity__gt=0)
    seller_group = None
    is_seller = vendors_service.is_vendor(user)
    can_have_balance = vendors_service.can_have_balance(user)

    template_name = "dashboard/user_detail.html"
    page_title = "User Details - " + settings.SITE_NAME
    context['page_title'] = page_title
    context['user_instance'] = user
    context['product_list'] = product_list
    context['is_seller'] = is_seller
    context['can_have_balance'] = can_have_balance
    context['has_balance'] = hasattr(user, 'balance') and user.balance is not None
    context.update(get_view_permissions(request.user))
    context['can_delete'] = PermissionManager.user_can_delete_user(request.user)
    context['can_update'] = PermissionManager.user_can_change_user(request.user)
    return render(request,template_name, context)


@login_required
def reset_vendor(request, pk=None):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    if not PermissionManager.user_can_view_user(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    context = {}
    #queryset = User.objects.select_related('account')
    user = get_object_or_404(User, pk=pk)
    
    seller_group = None
    is_seller = vendors_service.is_vendor(user)
    if is_seller:
        flag = vendors_service.reset_vendor(user)
        if flag:
            messages.success(request, f"Vendor \"{user.username}\" reset")
            logger.info(f"Vendor \"{user.username}\" reset")
        else:
            messages.error(request, f"Vendor \"{user.username}\" could not be reset")
            logger.error(f"Vendor \"{user.username}\" could not be reset")

    return redirect('dashboard:user-detail', pk=pk)



@login_required
def update_vendor_products(request, pk=None):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    if not PermissionManager.user_can_view_user(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    context = {}
    #queryset = User.objects.select_related('account')
    user = get_object_or_404(User, pk=pk)
    
    seller_group = None
    is_seller = vendors_service.is_vendor(user)
    if is_seller:
        flag = vendors_service.update_sold_product(user)
        if flag:
            messages.success(request, "Updated vendor Sold products")
            logger.info("Updated Vendor sold products")
        else:
            messages.error(request, "Vendor sold products could not be updated")
            logger.error("Vendor sold products could not be updated")

    return redirect('dashboard:user-detail', pk=pk)


@login_required
def create_vendor_balance(request, pk=None):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    if not PermissionManager.user_can_view_user(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    user = get_object_or_404(User, pk=pk)

    if Balance.objects.filter(user=user).exists():
        messages.warning(request, f"User {user.username} already has a Balance")
    else:
        Balance.objects.create(name=f'Balance {user.username}', user=user)
        messages.success(request, f"Balance created for User {user.username}")
    return redirect('dashboard:user-detail', pk=user.pk)

@login_required
def users_delete(request):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_delete_user(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if request.method != "POST":
        raise SuspiciousOperation('Bad request. Expected POST request but received a GET')
    
    postdata = utils.get_postdata(request)
    id_list = postdata.getlist('users')

    if len(id_list):
        user_list = list(map(int, id_list))
        User.objects.filter(id__in=user_list).delete()
        messages.success(request, f"Users \"{id_list}\" deleted")
        logger.info(f"Users \"{id_list}\" deleted by user {username}")
        
    else:
        messages.error(request, f"Users \"\" could not be deleted")
        logger.error(f"ID list invalid. Error : {id_list}")
    return redirect('dashboard:users')

@login_required
def user_delete(request, pk=None):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_delete_user(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if request.method != "POST":
        raise SuspiciousOperation('Bad request. Expected POST request but received a GET')
    
    postdata = utils.get_postdata(request)

    User.objects.filter(id=pk).delete()
    messages.success(request, f"Users \"{pk}\" deleted")
    logger.info(f"Users \"{pk}\" deleted by user {username}")
    return redirect('dashboard:users')

@login_required
def policies(request):
    username = request.user.username
    can_access_dashboard = PermissionManager.user_can_access_dashboard(request.user)
    if not can_access_dashboard:
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    can_view_policy = PermissionManager.user_can_view_policy(request.user)
    if not can_view_policy:
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    context = {}
    queryset = Policy.objects.all()
    template_name = "dashboard/policy_list.html"
    page_title = "Policies - " + settings.SITE_NAME
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, GLOBAL_CONF.PAGINATED_BY)
    try:
        list_set = paginator.page(page)
    except PageNotAnInteger:
        list_set = paginator.page(1)
    except EmptyPage:
        list_set = None
    context['page_title'] = page_title
    context['policies'] = list_set
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)


@login_required
def policy_update(request, policy_uuid=None):
    username = request.user.username
    can_access_dashboard = PermissionManager.user_can_access_dashboard(request.user)
    if not can_access_dashboard:
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    can_change_policy = PermissionManager.user_can_change_policy(request.user)
    if not can_change_policy:
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    page_title = _("Edit Policy")+ ' | ' + settings.SITE_NAME
    instance = get_object_or_404(Policy, policy_uuid=policy_uuid)
    template_name = "dashboard/policy_update.html"
    if request.method =="POST":
        form = PolicyForm(request.POST, instance=instance)
        if form.is_valid():
            logger.info("PolicyForm for instance %s is valid", form.cleaned_data['commission'])
            form.save()
            return redirect('dashboard:policies')
        else:
            logger.info("[failed] Edit PolicyForm commission : %s", request.POST.copy()['commission'])
            logger.info("Edit PolicyForm is not valid. Errors : %s", form.errors)
    
    form = PolicyForm(instance=instance)
    context = {
            'page_title':page_title,
            'template_name':template_name,
            'policy' : instance,
            'form': form,
            'can_change_policy' : can_change_policy
        }
    context.update(get_view_permissions(request.user))
    return render(request, template_name,context )



@login_required
def policy_remove(request, policy_uuid=None):
    # TODO Check if the user requesting the deletion has the permission
    username = request.user.username
    can_access_dashboard = PermissionManager.user_can_access_dashboard(request.user)
    if not can_access_dashboard:
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    can_delete_policy = PermissionManager.user_can_delete_policy(request.user)
    if not can_delete_policy:
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    deleted_count, extras = Policy.objects.filter(policy_uuid=policy_uuid).delete()
    if deleted_count > 0 :
        messages.add_message(request, messages.SUCCESS, 'Policy has been deleted')
        logger.debug("Policy deleted by User {}", request.user.username)
    
    else:
        messages.add_message(request, messages.ERROR, 'Policy could not be deleted')
        logger.error("Policy Delete failed. Action requested by User {}",request.user.username)
        
    return redirect('dashboard:policies')


@login_required
def policies_delete(request):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_delete_policy(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if request.method != "POST":
        raise SuspiciousOperation('Bad request. Expected POST request but received a GET')
    
    postdata = utils.get_postdata(request)
    id_list = postdata.getlist('policies')

    if len(id_list):
        instance_list = list(map(int, id_list))
        Policy.objects.filter(id__in=instance_list).delete()
        messages.success(request, f"Policies \"{instance_list}\" deleted")
        logger.info(f"Policies \"{instance_list}\" deleted by user {username}")
        
    else:
        messages.error(request, f"Policies could not be deleted")
        logger.error(f"ID list invalid. Error : {id_list}")
    return redirect('dashboard:policies')


@login_required
def policy_remove_all(request):
    # TODO Check if the user requesting the deletion has the permission
    username = request.user.username
    can_access_dashboard = PermissionManager.user_can_access_dashboard(request.user)
    if not can_access_dashboard:
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    can_delete_policy = PermissionManager.user_can_delete_policy(request.user)
    if not can_delete_policy:
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    deleted_count, extras = Policy.objects.delete()
    if deleted_count > 0 :
        messages.add_message(request, messages.SUCCESS, 'All Policies has been deleted')
        logger.debug("All Policies deleted by User {}", request.user.username)
    
    else:
        messages.add_message(request, messages.ERROR, 'All Policies could not be deleted')
        logger.error("All Policies Delete failed. Action requested by User {}",request.user.username)
        
    return redirect('dashboard:home')

@login_required
def policy_create(request):
    username = request.user.username
    can_access_dashboard = PermissionManager.user_can_access_dashboard(request.user)
    if not can_access_dashboard:
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    can_add_policy = PermissionManager.user_can_add_policy(request.user)
    if not can_add_policy:
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    page_title = _("Create Policy")+ ' | ' + settings.SITE_NAME
    template_name = "dashboard/policy_create.html"
    form = None
    if request.method =="POST":
        form = PolicyForm(request.POST)
        if form.is_valid():
            logger.info("PolicyForm for instance %s is valid", form.cleaned_data['commission'])
            form.save()
            return redirect('dashboard:policies')
        else:
            form = PolicyForm()
            logger.info("Edit PolicyForm is not valid. Errors : %s", form.errors)
    elif request.method == "GET":
        form = PolicyForm()

    context = {
            'page_title':page_title,
            'template_name':template_name,
            'form': form,
            'can_add_policy' : can_add_policy
        }
    
    context.update(get_view_permissions(request.user))
    return render(request, template_name,context )


@login_required
def policy_details(request, policy_uuid=None):
    username = request.user.username
    can_access_dashboard = PermissionManager.user_can_access_dashboard(request.user)
    if not can_access_dashboard:
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    can_view_policy = PermissionManager.user_can_view_policy(request.user)
    if not can_view_policy:
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    context = {}
    policy = get_object_or_404(Policy, policy_uuid=policy_uuid)
    template_name = "dashboard/policy_detail.html"
    page_title = "Policy Details - " + settings.SITE_NAME
    context['page_title'] = page_title
    context['policy'] = policy
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)


@login_required
def policy_groups(request):
    username = request.user.username
    can_access_dashboard = PermissionManager.user_can_access_dashboard(request.user)
    if not can_access_dashboard:
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    can_view_policy = PermissionManager.user_can_view_policy(request.user)
    can_add_policy = PermissionManager.user_can_add_policy(request.user)
    if not can_view_policy:
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    context = {}
    queryset = PolicyGroup.objects.all()
    template_name = "dashboard/policy_group_list.html"
    page_title = "Policy Group - " + settings.SITE_NAME
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, GLOBAL_CONF.PAGINATED_BY)
    try:
        list_set = paginator.page(page)
    except PageNotAnInteger:
        list_set = paginator.page(1)
    except EmptyPage:
        list_set = None
    context['page_title'] = page_title
    context['groups'] = list_set
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)


@login_required
def policy_group_create(request):
    username = request.user.username
    can_access_dashboard = PermissionManager.user_can_access_dashboard(request.user)
    if not can_access_dashboard:
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    can_add_policy = PermissionManager.user_can_add_policy(request.user)
    if not can_add_policy:
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    page_title = _("Create Policy Group") + ' | ' + settings.SITE_NAME
    template_name = "dashboard/policy_group_create.html"
    form = None
    if request.method =="POST":
        form = PolicyGroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard:policy-groups')
        else:
            logger.info("Edit PolicyGroupForm is not valid. Errors : %s", form.errors)
    elif request.method == "GET":
        form = PolicyGroupForm()

    context = {
            'page_title':page_title,
            'template_name':template_name,
            'form': form,
            'policies' : Policy.objects.all(),
            'can_add_policy' : can_add_policy
        }
    context.update(get_view_permissions(request.user))
    
    return render(request, template_name,context )

@login_required
def policy_group_update(request, group_uuid=None):
    username = request.user.username
    can_access_dashboard = PermissionManager.user_can_access_dashboard(request.user)
    if not can_access_dashboard:
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    can_change_policy = PermissionManager.user_can_change_policy(request.user)
    if not can_change_policy:
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    page_title = _("Edit Policy Group")+ ' | ' + settings.SITE_NAME
    instance = get_object_or_404(PolicyGroup, policy_group_uuid=group_uuid)
    template_name = "dashboard/policy_group_update.html"
    if request.method =="POST":
        form = PolicyGroupUpdateForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('dashboard:policy-groups')
        else:
            logger.info("Edit PolicyGroupUpdateForm is not valid. Errors : %s", form.errors)
    
    form = PolicyGroupForm(instance=instance)
    context = {
            'page_title':page_title,
            'template_name':template_name,
            'group' : instance,
            'form': form,
            'policies' : Policy.objects.all(),
            'can_change_policy' : can_change_policy
        }
    context.update(get_view_permissions(request.user))
    return render(request, template_name,context )


@login_required
def policy_group_update_members(request, group_uuid=None):
    username = request.user.username
    can_access_dashboard = PermissionManager.user_can_access_dashboard(request.user)
    if not can_access_dashboard:
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    can_change_policy = PermissionManager.user_can_change_policy(request.user)
    if not can_change_policy:
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    page_title = _("Edit Policy Group")+ ' | ' + settings.SITE_NAME
    instance = get_object_or_404(PolicyGroup, policy_group_uuid=group_uuid)
    template_name = "dashboard/policy_group_update.html"
    if request.method =="POST":
        form = PolicyGroupUpdateForm(request.POST, instance=instance)
        if form.is_valid():
            # user can not be members on more han one group at the same time.
            #old_members = instance.members.all()
            new_members = form.cleaned_data.get('members')
            logger.info('new members : %s', new_members)
            for u in new_members:
                u.policygroup_set.clear()
            
            instance.members.clear()
            form.save()
            messages.success(request, "Policy Group {} updated".format(instance.name))
            return redirect('dashboard:policy-groups')
        else:
            messages.error(request, "Policy Group {} could not updated. Invalid form".format(instance.name))
            logger.info("Edit PolicyGroupUpdateForm is not valid. Errors : %s", form.errors)
            return redirect(instance.get_dashboard_absolute_url())
    messages.error(request, "Invalid request")
    return redirect(instance.get_dashboard_absolute_url())
    """
    form = forms.PolicyGroupForm(instance=instance)
    context = {
            'page_title':page_title,
            'template_name':template_name,
            'policy_group' : instance,
            'form': form,
            'policies' : forms.Policy.objects.all(),
            'can_change_policy' : can_change_policy,
            'can_access_dashboard': can_access_dashboard
        }
    
    return render(request, template_name,context )
    """

@login_required
def policy_group_details(request, group_uuid=None):
    username = request.user.username
    can_access_dashboard = PermissionManager.user_can_access_dashboard(request.user)
    if not can_access_dashboard:
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    can_view_policy = PermissionManager.user_can_view_policy(request.user)
    if not can_view_policy:
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    context = {}
    group = get_object_or_404(PolicyGroup, policy_group_uuid=group_uuid)
    template_name = "dashboard/policy_group_detail.html"
    page_title = "Policy Group Details - " + settings.SITE_NAME
    context['page_title'] = page_title
    context['group'] = group
    context['members'] = group.members.all()
    context['users'] = User.objects.filter(is_active=True, is_superuser=False)
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)

@login_required
def policy_group_remove(request, group_uuid=None):
    # TODO Check if the user requesting the deletion has the permission
    username = request.user.username
    can_access_dashboard = PermissionManager.user_can_access_dashboard(request.user)
    if not can_access_dashboard:
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    can_delete_policy = PermissionManager.user_can_delete_policy(request.user)
    if not can_delete_policy:
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    deleted_count, extras = PolicyGroup.objects.filter(policy_group_uuid=group_uuid).delete()
    if deleted_count > 0 :
        messages.success(request, 'PolicyGroup has been deleted')
        logger.info("Policy Group deleted by User {}", request.user.username)
    
    else:
        messages.error(request, 'Policy Group could not be deleted')
        logger.error("Policy Group Delete failed. Action requested by User {}",request.user.username)
        
    return redirect('dashboard:policy-groups')


@login_required
def policy_groups_delete(request):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_delete_policy(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if request.method != "POST":
        raise SuspiciousOperation('Bad request. Expected POST request but received a GET')
    
    postdata = utils.get_postdata(request)
    id_list = postdata.getlist('policies-groups')

    if len(id_list):
        instance_list = list(map(int, id_list))
        PolicyGroup.objects.filter(id__in=instance_list).delete()
        messages.success(request, f"Policies Groups \"{instance_list}\" deleted")
        logger.info(f"Policies Groups \"{instance_list}\" deleted by user {username}")
        
    else:
        messages.error(request, f"Policies Groups could not be deleted")
        logger.error(f"ID list invalid. Error : {id_list}")
    return redirect('dashboard:policy-groups')


@login_required
def groups(request):
    username = request.user.username
    can_access_dashboard = PermissionManager.user_can_access_dashboard(request.user)
    if not can_access_dashboard:
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    can_view_group = PermissionManager.user_can_view_group(request.user)
    if not can_view_group:
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    context = {}
    
    #current_account = Account.objects.get(user=request.user)
    group_list = Group.objects.extra(select={'iname':'lower(name)'}).order_by('iname')
    template_name = "dashboard/group_list.html"
    page_title = "Groups" + " - " + settings.SITE_NAME
    page = request.GET.get('page', 1)
    paginator = Paginator(group_list, GLOBAL_CONF.PAGINATED_BY)
    try:
        group_set = paginator.page(page)
    except PageNotAnInteger:
        group_set = paginator.page(1)
    except EmptyPage:
        group_set = None
    context['page_title'] = page_title
    context['groups'] = group_set
    context['can_delete_group'] = PermissionManager.user_can_delete_group(request.user)
    context['can_update_group'] = PermissionManager.user_can_change_group(request.user)
    context['can_add_group'] = PermissionManager.user_can_add_group(request.user)
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)

@login_required
def group_detail(request, pk=None):
    username = request.user.username
    can_access_dashboard = PermissionManager.user_can_access_dashboard(request.user)
    if not can_access_dashboard:
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    can_view_group = PermissionManager.user_can_view_group(request.user)
    if not can_view_group:
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    context = {}
    group = get_object_or_404(Group, pk=pk)
    template_name = "dashboard/group_detail.html"
    page_title = "Group Detail" + " - " + settings.SITE_NAME
    context['page_title'] = page_title
    context['group'] = group
    context['can_delete_group'] = PermissionManager.user_can_delete_group(request.user)
    context['can_update_group'] = PermissionManager.user_can_change_group(request.user)
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)


@login_required
def group_update(request, pk=None):
    # TODO CHECK if the requesting User has the permission to update a group
    username = request.user.username
    can_access_dashboard = PermissionManager.user_can_access_dashboard(request.user)
    if not can_access_dashboard:
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    can_change_group = PermissionManager.user_can_change_group(request.user)
    if not can_change_group:
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    context = None
    page_title = 'Group Update'
    template_name = 'dashboard/group_update.html'
    group = get_object_or_404(Group, pk=pk)
    form = GroupFormCreation(instance=group)
    group_users = group.user_set.all()
    available_users = User.objects.exclude(pk__in=group_users.values_list('pk'))
    permissions = group.permissions.all()
    available_permissions = Permission.objects.exclude(pk__in=permissions.values_list('pk'))
    if request.method == 'POST':
        form = GroupFormCreation(request.POST, instance=group)
        users = request.POST.getlist('users')
        if form.is_valid() :
            logger.debug("Group form for update is valid")
            if form.has_changed():
                logger.debug("Group has changed")
            group = form.save()
            if users:
                logger.debug("adding %s users [%s] into the group", len(users), users)
                group.user_set.set(users)
            logger.debug("Saved users into the group %s",users)
            return redirect('dashboard:groups')
        else :
            logger.error("Error on editing the group. The form is invalid")
    
    context = {
            'page_title' : page_title,
            'form': form,
            'group': group,
            'users' : group_users,
            'available_users' : available_users,
            'permissions': permissions,
            'available_permissions' : available_permissions,
            'can_change_group' : can_change_group
    }
    context.update(get_view_permissions(request.user))
    return render(request, template_name, context)


@login_required
def group_create(request):
    username = request.user.username
    can_access_dashboard = PermissionManager.user_can_access_dashboard(request.user)
    if not can_access_dashboard:
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    can_add_group = PermissionManager.user_can_add_group(request.user)
    if not can_add_group:
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    context = None
    page_title = 'Group Creation'
    template_name = 'dashboard/group_create.html'
    available_permissions = Permission.objects.all()
    available_users = User.objects.all()
    form = GroupFormCreation()
    if request.method == 'POST':
        form = GroupFormCreation(request.POST)
        users = request.POST.getlist('users')
        if form.is_valid():
            logger.debug("Group Create : Form is Valid")
            group_name = form.cleaned_data.get('name', None)
            logger.debug('Creating a Group with the name {}'.format(group_name))
            if not Group.objects.filter(name=group_name).exists():
                group = form.save()
                messages.success(request, "The Group has been succesfully created")
                if users:
                    group.user_set.set(users)
                    logger.debug("Added users into the group %s",users)
                else :
                    logger.debug("Group %s created without users", group_name)

                return redirect('dashboard:groups')
            else:
                msg = "A Group with the given name {} already exists".format(group_name)
                messages.error(request, msg)
                logger.error(msg)
            
        else :
            messages.error(request, "The Group could not be created. Please correct the form")
            logger.error("Error on creating new Group Errors : %s", form.errors)
    
    context = {
            'page_title' : page_title,
            'form': form,
            'available_users' : available_users,
            'available_permissions': available_permissions,
            'can_add_group' : can_add_group
    }
    context.update(get_view_permissions(request.user))
    return render(request, template_name, context)


@login_required
def group_delete(request, pk=None):
    # TODO Check if the user requesting the deletion has the Group Delete permission
    username = request.user.username
    can_access_dashboard = PermissionManager.user_can_access_dashboard(request.user)
    if not can_access_dashboard:
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    can_delete_group = PermissionManager.user_can_delete_group(request.user)
    if not can_delete_group:
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    try:
        group = Group.objects.get(pk=pk)
        name = group.name
        messages.add_message(request, messages.SUCCESS, 'Group {} has been deleted'.format(name))
        group.delete()
        logger.debug("Group {} deleted by User {}", name, request.user.username)
        
    except Group.DoesNotExist:
        messages.add_message(request, messages.ERROR, 'Group could not be found. Group not deleted')
        logger.error("Group Delete : Group not found. Action requested by User {}",request.user.username)
        
    return redirect('dashboard:groups')


@login_required
def groups_delete(request):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_delete_group(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if request.method != "POST":
        raise SuspiciousOperation('Bad request. Expected POST request but received a GET')
    
    postdata = utils.get_postdata(request)
    id_list = postdata.getlist('groups')

    if len(id_list):
        instance_list = list(map(int, id_list))
        Group.objects.filter(id__in=instance_list).delete()
        messages.success(request, f"Groups \"{instance_list}\" deleted")
        logger.info(f"Groups \"{instance_list}\" deleted by user {username}")
        
    else:
        messages.error(request, f"Groups could not be deleted")
        logger.error(f"ID list invalid. Error : {id_list}")
    return redirect('dashboard:groups')


#######################################################
########            Permissions 

@login_required
def permissions(request):
    username = request.user.username
    can_access_dashboard = PermissionManager.user_can_access_dashboard(request.user)
    if not can_access_dashboard:
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied


    context = {}
    permission_list = Permission.objects.all()
    template_name = "dashboard/permission_list.html"
    page_title = "Permissions" + " - " + settings.SITE_NAME
    page = request.GET.get('page', 1)
    paginator = Paginator(permission_list, GLOBAL_CONF.PAGINATED_BY)
    try:
        permission_set = paginator.page(page)
    except PageNotAnInteger:
        permission_set = paginator.page(1)
    except EmptyPage:
        permission_set = None
    context['page_title'] = page_title
    context['permissions'] = permission_set
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)

@login_required
def permission_detail(request, pk=None):
    username = request.user.username
    can_access_dashboard = PermissionManager.user_can_access_dashboard(request.user)
    if not can_access_dashboard:
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    context = {}
    permission = get_object_or_404(Permission, pk=pk)
    template_name = "dashboard/permission_detail.html"
    page_title = "Permission Detail" + " - " + settings.SITE_NAME
    context['page_title'] = page_title
    context['permission'] = permission
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)


@login_required
def permission_update(request, pk=None):
    # TODO CHECK if the requesting User has the permission to update a permission
    username = request.user.username
    can_access_dashboard = PermissionManager.user_can_access_dashboard(request.user)
    if not can_access_dashboard:
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    context = None
    page_title = 'Permission Update'
    template_name = 'dashboard/permission_update.html'
    permission = get_object_or_404(Permission, pk=pk)
    form = GroupFormCreation(instance=permission)
    permission_users = permission.user_set.all()
    available_users = User.objects.exclude(pk__in=permission_users.values_list('pk'))

    if request.method == 'POST':
        form = GroupFormCreation(request.POST, instance=permission)
        users = request.POST.getlist('users')
        if form.is_valid() :
            logger.debug("Permission form for update is valid")
            if form.has_changed():
                logger.debug("Permission has changed")
            permission = form.save()
            if users:
                logger.debug("adding %s users [%s] into the permission", len(users), users)
                permission.user_set.set(users)
            logger.debug("Added permissions to users %s",users)
            return redirect('dashboard:permissions')
        else :
            logger.error("Error on editing the perssion. The form is invalid")
    
    context = {
            'page_title' : page_title,
            'form': form,
            'users' : permission_users,
            'available_users' : available_users,
            'permission': permission
    }
    context.update(get_view_permissions(request.user))
    return render(request, template_name, context)


@login_required
def permission_create(request):
    username = request.user.username
    can_access_dashboard = PermissionManager.user_can_access_dashboard(request.user)
    if not can_access_dashboard:
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    context = None
    page_title = 'Permission Creation'
    template_name = 'dashboard/permission_create.html'
    available_groups = Group.objects.all()
    available_users = User.objects.all()
    form = GroupFormCreation()
    if request.method == 'POST':
        form = GroupFormCreation(request.POST)
        users = request.POST.getlist('users')
        if form.is_valid():
            logger.debug("Permission Create : Form is Valid")
            perm_name = form.cleaned_data.get('name', None)
            perm_codename = form.cleaned_data.get('codename', None)
            logger.debug('Creating a Permission with the name {}'.format(perm_name))
            if not Permission.objects.filter(Q(name=perm_name) | Q(codename=perm_codename)).exists():
                perm = form.save()
                messages.add_message(request, messages.SUCCESS, "The Permission has been succesfully created")
                if users:
                    perm.user_set.set(users)
                    logger.debug("Permission %s given to users  %s",perm_name, users)
                else :
                    logger.debug("Permission %s created without users", perm_name)

                return redirect('dashboard:permissions')
            else:
                msg = "A Permission with the given name {} already exists".format(perm_name)
                messages.add_message(request, messages.ERROR, msg)
                logger.error(msg)
            
        else :
            messages.add_message(request, messages.ERROR, "The Permission could not be created. Please correct the form")
            logger.error("Error on creating new Permission : %s", form.errors)
    
    context = {
            'page_title' : page_title,
            'form': form,
            'available_users' : available_users,
            'available_groups': available_groups
    }
    context.update(get_view_permissions(request.user))
    return render(request, template_name, context)


@login_required
def permission_delete(request, pk=None):
    # TODO Check if the user requesting the deletion has the Group Delete permission
    username = request.user.username
    can_access_dashboard = PermissionManager.user_can_access_dashboard(request.user)
    if not can_access_dashboard:
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    try:
        perm = Permission.objects.get(pk=pk)
        name = perm.name
        messages.add_message(request, messages.SUCCESS, 'Permission {} has been deleted'.format(name))
        perm.delete()
        logger.debug("Permission {} deleted by User {}", name, request.user.username)
        
    except Permission.DoesNotExist:
        messages.add_message(request, messages.ERROR, 'Permission could not be found. Permission not deleted')
        logger.error("Permission Delete : Permission not found. Action requested by User {}",request.user.username)
        raise Http404('Permission does not exist')
        
    return redirect('dashboard:permissions')


@login_required
def create_account(request):
    username = request.user.username
    context = {}
    page_title = _('New User')
    template_name = 'dashboard/new_user.html'
    can_access_dashboard = PermissionManager.user_can_access_dashboard(request.user)
    if not can_access_dashboard:
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    can_view_user = PermissionManager.user_can_view_user(request.user)
    can_add_user = PermissionManager.user_can_add_user(request.user)
    if not (can_add_user and can_view_user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    if request.method == 'POST':
        name = request.POST['username']
        result = AccountService.process_registration_request(request)
        if result['user_created']:
            messages.success(request, _(f"User {name} created"))
            return redirect('dashboard:users')
        else:
            user_form = UserCreationForm(request.POST)
            account_form = AccountCreationForm(request.POST)
            user_form.is_valid()
            account_form.is_valid()
    else:
        user_form = UserCreationForm()
        account_form = AccountCreationForm()
    context.update(get_view_permissions(request.user))
    context['can_add_user'] = can_add_user
    context['user_form'] = user_form
    context['account_form'] = account_form
    return render(request, template_name, context)



@login_required
def payment_requests(request):
    username = request.user.username
    can_access_dashboard = PermissionManager.user_can_access_dashboard(request.user)
    if not can_access_dashboard:
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    can_view_payment = PermissionManager.user_can_view_payment(request.user)
    if not can_view_payment:
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    context = {}
    #current_account = Account.objects.get(user=request.user)
    queryset = PaymentRequest.objects.all().order_by('-created_at')
    template_name = "dashboard/payment_request_list.html"
    page_title = "Payments Requests - " + settings.SITE_NAME
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, GLOBAL_CONF.PAGINATED_BY)
    try:
        request_set = paginator.page(page)
    except PageNotAnInteger:
        request_set = paginator.page(1)
    except EmptyPage:
        request_set = None
    context['page_title'] = page_title
    context['requests'] = request_set
    context['can_delete_payment'] = PermissionManager.user_can_delete_payment(request.user)
    context['can_update_payment'] = PermissionManager.user_can_change_payment(request.user)
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)


@login_required
def payment_request_details(request, request_uuid=None):
    username = request.user.username
    can_access_dashboard = PermissionManager.user_can_access_dashboard(request.user)
    if not can_access_dashboard:
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    can_view_payment = PermissionManager.user_can_view_payment(request.user)
    if not can_view_payment:
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    context = {}
    logger.debug("(payment_request_details) - querying Payment request object")
    payment_request = get_object_or_404(PaymentRequest, request_uuid=request_uuid)
    logger.debug("[OK] querying Payment request object")
    template_name = "dashboard/payment_request_detail.html"
    page_title = "Payment Details - " + settings.SITE_NAME
    context['page_title'] = page_title
    context['payment_request'] = payment_request
    context['can_delete_payment'] = PermissionManager.user_can_delete_payment(request.user)
    context['can_update_payment'] = PermissionManager.user_can_change_payment(request.user)
    logger.debug("(payment_request_details) - Updating context object")
    context.update(get_view_permissions(request.user))
    logger.debug("[OK] (payment_request_details) - Updating context object")
    return render(request,template_name, context)



@login_required
def coupons(request):
    username = request.user.username
    can_access_dashboard = PermissionManager.user_can_access_dashboard(request.user)
    if not can_access_dashboard:
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    can_view_coupon = PermissionManager.user_can_view_coupon(request.user)
    if not can_view_coupon:
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    context = {}
    #current_account = Account.objects.get(user=request.user)
    queryset = Coupon.objects.all().order_by('-created_at')
    template_name = "dashboard/coupon_list.html"
    page_title = "Coupon - " + settings.SITE_NAME
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, GLOBAL_CONF.PAGINATED_BY)
    try:
        request_set = paginator.page(page)
    except PageNotAnInteger:
        request_set = paginator.page(1)
    except EmptyPage:
        request_set = None
    context['page_title'] = page_title
    context['coupon_list'] = request_set
    context['can_delete_coupon'] = PermissionManager.user_can_delete_coupon(request.user)
    context['can_update_coupon'] = PermissionManager.user_can_change_coupon(request.user)
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)


@login_required
def coupon_detail(request, coupon_uuid=None):
    username = request.user.username
    can_access_dashboard = PermissionManager.user_can_access_dashboard(request.user)
    if not can_access_dashboard:
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    can_view_coupon = PermissionManager.user_can_view_coupon(request.user)
    if not can_view_coupon:
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    context = {}
    coupon = get_object_or_404(Coupon, coupon_uuid=coupon_uuid)
    template_name = "dashboard/coupon_detail.html"
    page_title = "Coupon" + " - " + settings.SITE_NAME
    context['page_title'] = page_title
    context['coupon'] = coupon
    context['can_delete_coupon'] = PermissionManager.user_can_delete_coupon(request.user)
    context['can_update_coupon'] = PermissionManager.user_can_change_coupon(request.user)
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)


@login_required
def coupon_create(request):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_add_coupon(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    template_name = 'dashboard/coupon_create.html'
    page_title = _('New Coupon')
    
    form = None
    username = request.user.username
    sellers = User.objects.none()
    try:
        seller_group = Group.objects.get(name=Constants.SELLER_GROUP)
        sellers = seller_group.user_set.all()
    except ObjectDoesNotExist as e:
        pass
    if request.method == 'POST':
        postdata = utils.get_postdata(request)
        form = CouponForm(postdata)
        if form.is_valid():
            coupon = form.save()
            messages.success(request, _('New Coupon created'))
            logger.info(f'New Coupon added by user \"{username}\"')
            return redirect(coupon.get_dashboard_url())
        else:
            messages.error(request, _('Coupon not created'))
            logger.error(f'Error on creating new Coupon. Action requested by user \"{username}\"')
    else:
        form = CouponForm()
    context = {
        'page_title': page_title,
        'form' : form,
        'sellers' : sellers
    }
    context.update(get_view_permissions(request.user))
    return render(request, template_name, context)


@login_required
def coupon_update(request, coupon_uuid=None):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_change_coupon(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    template_name = 'dashboard/coupon_update.html'
    page_title = _('Coupon Update')
    
    form = None
    username = request.user.username
    coupon = get_object_or_404(Coupon, coupon_uuid=coupon_uuid)
    sellers = User.objects.none()
    try:
        seller_group = Group.objects.get(name=Constants.SELLER_GROUP)
        sellers = seller_group.user_set.all()
    except ObjectDoesNotExist as e:
        pass
    if request.method == 'POST':
        postdata = utils.get_postdata(request)
        activated = postdata.get('is_active')
        logger.debug("Coupon Postdata")
        utils.show_dict_contents(postdata, "Coupon Postdata")
        
        if postdata.get('is_active') == 'on':
            postdata['activated_by'] = request.user.pk
            postdata['activated_at'] = timezone.now()
            
        form = CouponForm(postdata, instance=coupon)
        if form.is_valid():
            coupon = form.save()
            messages.success(request, _('Coupon updated'))
            logger.info(f'Coupon updated by user \"{username}\" - coupon is_active = \"{coupon.is_active}\"')
            return redirect('dashboard:coupon-detail', coupon_uuid=coupon_uuid)
        else:
            messages.error(request, _('Coupon not updated'))
            logger.error(f'Error on updated Coupon. Action requested by user \"{username}\"')
            logger.error(form.errors)
    else:
        form = CouponForm(instance=coupon)
    context = {
        'page_title': page_title,
        'form' : form,
        'coupon': coupon,
        'sellers': sellers
    }
    context.update(get_view_permissions(request.user))
    return render(request, template_name, context)


@login_required
def coupon_delete(request, coupon_uuid=None):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_delete_coupon(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if request.method != "POST":
        raise SuspiciousOperation('Bad request')

    coupon = get_object_or_404(Coupon, coupon_uuid=coupon_uuid)
    coupon_name = coupon.name
    coupon.delete()
    logger.info(f'Coupon \"{coupon_name}\" deleted by user \"{request.user.username}\"')
    messages.success(request, _('Coupon deleted'))
    return redirect('dashboard:coupons')



@login_required
def coupons_delete(request):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_delete_coupon(request.user):
        logger.warning(f"PermissionDenied to user \"{username}\" for path \"{request.path}\"")
        raise PermissionDenied
    if request.method != "POST":
        raise SuspiciousOperation('Bad request')
    postdata = utils.get_postdata(request)
    id_list = postdata.getlist('coupons')

    if len(id_list):
        coupon_list = list(map(int, id_list))
        Coupon.objects.filter(id__in=coupon_list).delete()
        messages.success(request, f"Coupons \"{coupon_list}\" deleted")
        logger.info(f"Coupon \"{coupon_list}\" deleted by user {username}")
        
    else:
        messages.error(request, f"Coupons  could not be deleted")
        logger.error(f"Coupon Delete : ID list invalid. Error : {id_list}")
    return redirect('dashboard:coupons')





@login_required
def product_types(request):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_view_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    template_name = 'dashboard/product_type_list.html'
    page_title = _('ProductTypes')
    if request.method != 'GET':
        return HttpResponseBadRequest('Bad request')

    queryset = ProductType.objects.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, GLOBAL_CONF.PAGINATED_BY)
    try:
        list_set = paginator.page(page)
    except PageNotAnInteger:
        list_set = paginator.page(1)
    except EmptyPage:
        list_set = None
    context = {
        'page_title': page_title,
        'product_type_list': list_set
    }
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)


@login_required
def product_type_create(request):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_add_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    template_name = 'dashboard/product_type_create.html'
    page_title = _('New ProductType')
    
    form = None
    username = request.user.username
    if request.method == 'POST':
        postdata = utils.get_postdata(request)
        form = ProductTypeForm(postdata)
        if form.is_valid():
            product_type = form.save()
            messages.success(request, _('New ProductType created'))
            logger.info(f'New ProductType added by user \"{username}\"')
            return redirect('dashboard:product-types')
        else:
            messages.error(request, _('ProductType not created'))
            logger.error(f'Error on creating new ProductType. Action requested by user \"{username}\"')
            logger.error(form.errors.items())
    else:
        form = ProductTypeForm()
    context = {
        'page_title': page_title,
        'type_attributes' : ProductTypeAttribute.objects.all(),
        'form' : form
    }
    context.update(get_view_permissions(request.user))
    return render(request, template_name, context)

@login_required
def product_type_detail(request, type_uuid=None):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_view_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    template_name = 'dashboard/product_type_detail.html'
    page_title = _('ProductType Detail')
    
    if request.method != "GET":
        raise SuspiciousOperation('Bad request')

    product_type = get_object_or_404(models.ProductType, type_uuid=type_uuid)
    product_list = Product.objects.filter(product_type=product_type)
    context = {
        'page_title': page_title,
        'product_list': product_list,
        'product_type': product_type,
        'attribute_list': product_type.attributes.all(),
        'ATTRIBUTE_TYPE': Catalog_Constants.ATTRIBUTE_TYPE
    }
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)

@login_required
def product_type_update(request, type_uuid=None):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_change_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    template_name = 'dashboard/product_type_update.html'
    page_title = _('ProductType Update')
    
    form = None
    username = request.user.username
    product_type = get_object_or_404(models.ProductType, type_uuid=type_uuid)
    if request.method == 'POST':
        postdata = utils.get_postdata(request)
        form = ProductTypeForm(postdata, instance=product_type)
        if form.is_valid():
            product_type = form.save()
            messages.success(request, _('ProductTyppe updated'))
            logger.info(f'ProductType updated by user \"{username}\"')
            return redirect('dashboard:product-type-detail', type_uuid=type_uuid)
        else:
            messages.error(request, _('ProductType not updated'))
            logger.error(f'Error on updated ProductType. Action requested by user \"{username}\"')
            logger.error(form.errors.items())
    else:
        form = ProductTypeForm(instance=product_type)
    context = {
        'page_title': page_title,
        'form' : form,
        'product_type': product_type,
        'attributes' : ProductAttribute.objects.exclude(id__in=product_type.attributes.all()),
        'type_attributes' : ProductTypeAttribute.objects.exclude(id__in=product_type.type_attributes.all())
    }
    context.update(get_view_permissions(request.user))
    return render(request, template_name, context)


@login_required
def product_type_delete(request, type_uuid=None):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_delete_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if request.method != "POST":
        raise SuspiciousOperation('Bad request')

    product_type = get_object_or_404(models.ProductType, type_uuid=type_uuid)
    product_type_name = product_type.name
    product_type.delete()
    logger.info(f'ProductType \"{product_type_name}\" deleted by user \"{request.user.username}\"')
    messages.success(request, _('ProductType deleted'))
    return redirect('dashboard:product-types')


@login_required
def product_types_delete(request):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_delete_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if request.method != "POST":
        raise SuspiciousOperation('Bad request. Expected POST request but received a GET')
    
    postdata = utils.get_postdata(request)
    id_list = postdata.getlist('product_types')

    if len(id_list):
        product_type_list = list(map(int, id_list))
        ProductType.objects.filter(id__in=product_type_list).delete()
        messages.success(request, f"ProductType \"{product_type_list}\" deleted")
        logger.info(f"ProductType\"{product_type_list}\" deleted by user {username}")
        
    else:
        messages.error(request, f"ProductType could not be deleted")
        logger.error(f"ID list invalid. Error : {id_list}")
    return redirect('dashboard:product-types')


@login_required
def product_type_products(request, type_uuid=None):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_view_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    template_name = 'dashboard/brand_product_list.html'
    page_title = _('Product Type Products')
    
    if request.method != 'GET':
        return HttpResponseBadRequest('Bad request')

    product_type = get_object_or_404(models.Brand, type_uuid=type_uuid)
    queryset = models.Product.objects.filter(product_type=product_type)
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, GLOBAL_CONF.PAGINATED_BY)
    try:
        list_set = paginator.page(page)
    except PageNotAnInteger:
        list_set = paginator.page(1)
    except EmptyPage:
        list_set = None
    context = {
        'page_title': page_title,
        'product_list': list_set,
        'product_type': product_type
    }
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)

## PRODUCT TYPE ATTRIBUTES

@login_required
def product_type_attributes(request):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_view_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    template_name = 'dashboard/product_type_attribute_list.html'
    page_title = _('ProductType Attributes')
    if request.method != 'GET':
        return HttpResponseBadRequest('Bad request')

    queryset = ProductTypeAttribute.objects.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, GLOBAL_CONF.PAGINATED_BY)
    try:
        list_set = paginator.page(page)
    except PageNotAnInteger:
        list_set = paginator.page(1)
    except EmptyPage:
        list_set = None
    context = {
        'page_title': page_title,
        'type_attribute_list': list_set,
        'ATTRIBUTE_TYPE': Catalog_Constants.ATTRIBUTE_TYPE
    }
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)


@login_required
def product_type_attribute_create(request):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_add_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    template_name = 'dashboard/product_type_attribute_create.html'
    page_title = _('New Product Type Attribute')
    
    form = None
    username = request.user.username
    if request.method == 'POST':
        postdata = utils.get_postdata(request)
        form = ProductTypeAttributeForm(postdata)
        if form.is_valid():
            attribute_type = form.save()
            messages.success(request, _('New ProductTypeAttribute created'))
            logger.info(f'New ProductTypeAttribute added by user \"{username}\"')
            return redirect('dashboard:product-type-attributes')
        else:
            messages.error(request, _('ProductType not created'))
            logger.error(f'Error on creating new ProductType. Action requested by user \"{username}\"')
            logger.error(form.errors.items())
    else:
        form = ProductTypeAttributeForm()
    context = {
        'page_title': page_title,
        'ATTRIBUTE_TYPE': Catalog_Constants.ATTRIBUTE_TYPE,
        'form' : form
    }
    context.update(get_view_permissions(request.user))
    return render(request, template_name, context)

@login_required
def product_type_attribute_detail(request, type_attribute_uuid=None):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_view_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    template_name = 'dashboard/product_type_attribute_detail.html'
    page_title = _('ProductTypeAttribute Detail')
    
    if request.method != "GET":
        raise SuspiciousOperation('Bad request')

    type_attribute = get_object_or_404(ProductTypeAttribute, type_attribute_uuid=type_attribute_uuid)
    attributes = ProductAttribute.objects.filter(name=type_attribute.name, display_name=type_attribute.display_name)
    #product_list = Product.objects.filter(product_type=product_type)
    context = {
        'page_title': page_title,
        #'product_list': product_list,
        'ATTRIBUTE_TYPE': Catalog_Constants.ATTRIBUTE_TYPE,
        'attribute_list': attributes,
        'type_attribute': type_attribute
    }
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)

@login_required
def product_type_attribute_update(request, type_attribute_uuid=None):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_change_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    template_name = 'dashboard/product_type_attribute_update.html'
    page_title = _('ProductTypeAttribute Update')
    
    form = None
    username = request.user.username
    type_attribute = get_object_or_404(ProductTypeAttribute, type_attribute_uuid=type_attribute_uuid)
    if request.method == 'POST':
        postdata = utils.get_postdata(request)
        form = ProductTypeAttributeForm(postdata, instance=type_attribute)
        if form.is_valid():
            type_attribute = form.save()
            messages.success(request, _('ProductTypeAttribute updated'))
            logger.info(f'ProductTypeAttribute updated by user \"{username}\"')
            return redirect('dashboard:product-type-attributes')
        else:
            messages.error(request, _('ProductTypeAttribute not updated'))
            logger.error(f'Error on updated ProductTypeAttribute. Action requested by user \"{username}\"')
            logger.error(form.errors.items())
    else:
        form = ProductTypeAttributeForm(instance=type_attribute)
    context = {
        'page_title': page_title,
        'form' : form,
        'ATTRIBUTE_TYPE': Catalog_Constants.ATTRIBUTE_TYPE,
        'attribute_list': type_attribute.attributes.all(),
        'type_attribute': type_attribute
    }
    context.update(get_view_permissions(request.user))
    return render(request, template_name, context)


@login_required
def product_type_attribute_delete(request, type_attribute_uuid=None):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_delete_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if request.method != "POST":
        raise SuspiciousOperation('Bad request')

    product_type = get_object_or_404(ProductTypeAttribute, type_attribute_uuid=type_attribute_uuid)
    product_type_name = product_type.name
    product_type.delete()
    logger.info(f'ProductTypeAttribute \"{product_type_name}\" deleted by user \"{request.user.username}\"')
    messages.success(request, _('ProductTypeAttribute deleted'))
    return redirect('dashboard:product-type-attributes')


@login_required
def product_type_attributes_delete(request):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_delete_product(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if request.method != "POST":
        raise SuspiciousOperation('Bad request. Expected POST request but received a GET')
    
    postdata = utils.get_postdata(request)
    id_list = postdata.getlist('type_attributes')

    if len(id_list):
        type_list = list(map(int, id_list))
        ProductTypeAttribute.objects.filter(id__in=type_list).delete()
        messages.success(request, f"ProductTypeAttribute \"{type_list}\" deleted")
        logger.info(f"ProductTypeAttribute \"{type_list}\" deleted by user {username}")
        
    else:
        messages.error(request, f"ProductTypeAttribute could not be deleted")
        logger.error(f"ID list invalid. Error : {id_list}")
    return redirect('dashboard:product-type-attributes')



@login_required
def payment_method_create(request):
    template_name = 'dashboard/payment_method_create.html'
    page_title = _('New Payment Method')
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_add_payment(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    context = {
        'page_title': page_title,
        'ORDER_PAYMENT_MODE' : Order_Constants.ORDER_PAYMENT_MODE
    }
    if request.method == 'POST':
        postdata = utils.get_postdata(request)
        payment_method, created = orders_service.create_payment_method(postdata)
        if created:
            messages.success(request,_('New PaymentMethod {payment_method} created'))
            logger.info(f'[ OK ] New PaymentMethod {payment_method} added by user {request.user.username}' )
            return redirect('dashboard:payment-methods')
        else:
            messages.error(request,_('PaymentMethod not created'))
            logger.error(f'[ NOT OK ] Error on adding New PaymentMethod by user {request.user.username}. Errors : {form.errors}' )

    form = PaymentMethodForm()
    context['form'] = form
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)
    



@login_required
def payment_methods(request):
    template_name = 'dashboard/payment_method_list.html'
    page_title = _('Payment Method List')
    
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_view_payment(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    context = {
        'page_title': page_title,
        'ORDER_PAYMENT_MODE' : Order_Constants.ORDER_PAYMENT_MODE
    }
    queryset = orders_service.get_payment_methods()
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, GLOBAL_CONF.PAGINATED_BY)
    try:
        list_set = paginator.page(page)
    except PageNotAnInteger:
        list_set = paginator.page(1)
    except EmptyPage:
        list_set = None
    context['payment_method_list'] = list_set
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)

@login_required
def payment_method_detail(request, method_uuid=None):
    template_name = 'dashboard/payment_method_detail.html'
    page_title = _('Payment Method')
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_view_payment(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    context = {
        'page_title': page_title
    }

    payment_method = get_object_or_404(PaymentMethod, method_uuid=method_uuid)
    context['payment_method'] = payment_method
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)

@login_required
def payment_method_update(request, method_uuid):
    template_name = 'dashboard/payment_method_update.html'
    page_title = _('Edit Payment Method')
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_change_payment(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    payment_method = get_object_or_404(PaymentMethod, method_uuid=method_uuid)
    if request.method == 'POST':
        postdata = utils.get_postdata(request)
        utils.show_dict_contents(postdata, "PAYMENT METHOD POSTDATA ")
        payment_method, updated = orders_service.update_payment_method(postdata, payment_method)
        if updated :
            messages.success(request,_('PaymentMethod updated'))
            logger.info(f'[ OK ] PaymentMethod \"{payment_method}\" updated by user {request.user.username}' )
            return redirect(payment_method.get_dashboard_url())
        else:
            messages.error(request,_('Error when updating PaymentMethod'))
            logger.error(f'[ NOT OK ] Error on updating PaymentMethod \"{payment_method}\" added by user {request.user.username}' )

    form = PaymentMethodForm(instance=payment_method)
    context = {
        'page_title': page_title,
        'form' : form,
        'payment_method':payment_method,
        'ORDER_PAYMENT_MODE' : Order_Constants.ORDER_PAYMENT_MODE
    }
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)


@login_required
def payment_method_delete(request, method_uuid):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_delete_payment(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    if request.method != "POST":
        raise SuspiciousOperation('Bad request. POST request expected but received a GET request')
    payment_method = get_object_or_404(PaymentMethod, method_uuid=method_uuid)
    PaymentMethod.objects.filter(pk=payment_method.pk).delete()
    return redirect('dashboard:payment-methods')


@login_required
def payment_methods_delete(request):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_delete_payment(request.user):
        logger.warning(f"PermissionDenied to user \"{username}\" for path \"{request.path}\"")
        raise PermissionDenied
    if request.method != "POST":
        raise SuspiciousOperation('Bad request')
    postdata = utils.get_postdata(request)
    id_list = postdata.getlist('payment_methods')

    if len(id_list):
        method_list = list(map(int, id_list))
        PaymentMethod.objects.filter(id__in=method_list).delete()
        messages.success(request, f"PaymentMethod \"{method_list}\" deleted")
        logger.info(f"PaymentMethod \"{method_list}\" deleted by user {username}")
        
    else:
        messages.error(request, f"PaymentMethod  could not be deleted")
        logger.error(f"ID list invalid. Error : {id_list}")
    return redirect('dashboard:payment-methods')



@login_required
def addressbook(request):
    template_name = "dashboard/addressbook.html"
    username = request.user.username
    context = {}
    queryset = Address.objects.all().order_by('-created_at')
    page_title = _("Addresses") + " - " + settings.SITE_NAME
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, GLOBAL_CONF.PAGINATED_BY)
    try:
        list_set = paginator.page(page)
    except PageNotAnInteger:
        list_set = paginator.page(1)
    except EmptyPage:
        list_set = None
    context['page_title'] = page_title
    context['address_list'] = list_set
    return render(request,template_name, context)


@login_required
def address_detail(request, address_uuid=None):
    template_name = 'dashboard/address_detail.html'
    username = request.user.username
    page_title = _('Address')

    address = get_object_or_404(Address, address_uuid=address_uuid)
    context = {
        'page_title': page_title,
        'address': address,
    }
    return render(request,template_name, context)


@login_required
def address_update(request, address_uuid=None):
    username = request.user.username
    template_name = 'dashboard/address_update.html'
    page_title = _('Address Update')
    context = {
        'page_title': page_title,
    }
    obj = get_object_or_404(Address, address_uuid=address_uuid)
    username = request.user.username
    if request.method == 'POST':
        postdata = utils.get_postdata(request)
        updated_address = addressbook_service.update_address(obj, postdata)
        if updated_address:
            messages.success(request, _('Address updated'))
            logger.info(f'address {updated_address} updated by user \"{username}\"')
            return redirect('dashboard:address-detail', address_uuid=address_uuid)
        else:
            messages.error(request, _('Address not updated'))
            logger.error(f'Error on updating address. Action requested by user \"{username}\"')

    context['address'] = obj
    context['user_list'] = User.objects.filter(is_superuser=False)
    context['ADDRESS_TYPES'] = Addressbook_Constants.ADDRESS_TYPES
    return render(request, template_name, context)


@login_required
def address_delete(request, address_uuid=None):
    username = request.user.username
    obj = get_object_or_404(Address, address_uuid=address_uuid)
    Address.objects.filter(pk=obj.pk).delete()
    logger.info(f'Address \"{obj}\" deleted by user \"{request.user.username}\"')
    messages.success(request, _('Address deleted'))
    return redirect('dashboard:addressbook')


@login_required
def addresses_delete(request):
    username = request.user.username
    
    postdata = utils.get_postdata(request)
    id_list = postdata.getlist('addresses')

    if len(id_list):
        address_id_list = list(map(int, id_list))
        Address.objects.filter(id__in=address_id_list).delete()
        messages.success(request, f"Addresses \"{id_list}\" deleted")
        logger.info(f"Addresses \"{id_list}\" deleted by user {username}")
        
    else:
        messages.error(request, f"Addresses \"{id_list}\" could not be deleted")
        logger.error(f"ID list invalid. Error : {id_list}")
    return redirect('dashboard:addressbook')