from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied, SuspiciousOperation

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
from lyshop import utils, settings
from dashboard.forms import (AccountForm, GroupFormCreation, PolicyForm, PolicyGroupForm, 
    PolicyGroupUpdateForm, PolicyGroupUpdateMembersForm, TokenForm
)
from accounts.forms import AccountCreationForm, UserCreationForm
from accounts.account_services import AccountService
from catalog.models import (
    Product, Brand, Category, ProductAttribute, ProductVariant, Policy, PolicyGroup, PolicyMembership, ProductImage
)
from orders.models import Order, OrderItem, PaymentRequest
from catalog.forms import (BrandForm, ProductAttributeForm, 
    ProductForm, ProductVariantForm, CategoryForm, ProductImageForm, AttributeForm, AddAttributeForm,
    DeleteAttributeForm, CategoriesDeleteForm
)
from cart.models import Coupon
from cart.forms import CouponForm
from catalog import models
from dashboard import analytics
import json
import logging

logger = logging.getLogger(__name__)

# Create your views here.

#TODO : Add Required Login decoators


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
        postdata = utils.get_postdata(request)
        form = CategoryForm(postdata)
        if form.is_valid():
            category = form.save()
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

    queryset = models.Category.objects.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, 10)
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
        postdata = utils.get_postdata(request)
        form = CategoryForm(postdata, instance=category)
        if form.is_valid():
            category = form.save()
            messages.success(request,_('Category updated'))
            logger.info(f'[ OK ] Category \"{category.name}\" updated by user {request.user.username}' )
            return redirect(category.get_dashboard_url())
        else:
            messages.error(request,_('Error when updating category'))
            logger.error(f'[ NOT OK ] Error on updating Category \"{category.name}\" added by user {request.user.username}' )
    elif request.method == 'GET':
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
    paginator = Paginator(queryset, 10)
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
def create_product(request):
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
    form = None
    
    username = request.user.username
    if request.method == 'POST':
        postdata = utils.get_postdata(request)
        form = ProductForm(postdata)
        if form.is_valid():
            product = form.save()
            messages.success(request, _('New Product created'))
            logger.info(f'New product added by user \"{username}\"')
            return redirect('dashboard:products')
        else:
            messages.error(request, _('Product not created'))
            logger.error(f'Error on creating new product. Action requested by user \"{username}\"')
    else:
        form = ProductForm()
    context['form'] = form
    context['brand_list'] = models.Brand.objects.all()
    context['category_list'] = models.Category.objects.all()
    context['user_list'] = User.objects.all()
    context['gender_list'] = models.Product.GENDER
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
    queryset = Order.objects.all()
    template_name = "dashboard/order_list.html"
    page_title = _("Dashboard Orders") + " - " + settings.SITE_NAME
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, utils.PAGINATED_BY)
    try:
        list_set = paginator.page(page)
    except PageNotAnInteger:
        list_set = paginator.page(1)
    except EmptyPage:
        list_set = None
    context['page_title'] = page_title
    context['orders'] = list_set
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
        'orderItems': orderItems,
    }
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)


@login_required
def order_update(request, order_uuid=None):
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

    queryset = models.Product.objects.filter(is_active=True)
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, 10)
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
        if form.is_valid():
            product = form.save()
            messages.success(request, _('Product updated'))
            logger.info(f'product {product.name} updated by user \"{username}\"')
            return redirect('dashboard:product-detail', product_uuid=product_uuid)
        else:
            messages.error(request, _('Product not updated'))
            logger.error(f'Error on updating product. Action requested by user \"{username}\"')
            logger.error(form.errors)
    else:
        form = ProductForm(instance=product)
    context['form'] = form
    context['product'] = product
    context['brand_list'] = models.Brand.objects.all()
    context['category_list'] = models.Category.objects.all()
    context['user_list'] = User.objects.all()
    context['gender_list'] = models.Product.GENDER
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
    if request.method == "POST":
        postdata = utils.get_postdata(request)
        
        form = ProductImageForm(postdata, request.FILES)
        if form.is_valid():
            logger.info("submitted product image form is valide")
            logger.info("saving submitted product image form")
            form.save()
            logger.info("submitted idcard form saved")
            return redirect('dashboard:product-detail', product_uuid=product_uuid)
            
        else:
            logger.error("The idcard form is not valide. Error : %s", form.non_field_errors)
    else:
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
    image = get_object_or_404(ProductImage, image_uuid=image_uuid)

    template_name = "dashboard/product_image_detail.html"
    page_title = "Product Image" + " - " + settings.SITE_NAME
    context['page_title'] = page_title
    context['image'] = image
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

    image = get_object_or_404(ProductImage, image_uuid=image_uuid)
    product = image.product
    ProductImage.objects.filter(pk=image.pk).delete()
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
    queryset = ProductImage.objects.filter(product__product_uuid=product_uuid)
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, 10)
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
    context['attribute_types'] = ProductAttribute.ATTRIBUTE_TYPE
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
    attr_types = [v for k,v in ProductAttribute.ATTRIBUTE_TYPE]
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
        'attribute_types' : ProductAttribute.ATTRIBUTE_TYPE,
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
        form = ProductVariantForm(postdata, instance=variant)
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
        'attribute_types': ProductAttribute.ATTRIBUTE_TYPE
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
    
    form = None
    username = request.user.username
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
    else:
        form = ProductVariantForm()
    context = {
        'page_title': page_title,
        'formset' : attribute_formset(),
        'variant' : variant
    }
    context['attribute_formset'] = attribute_formset
    context['attribute_types'] = ProductAttribute.ATTRIBUTE_TYPE
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
        'product_list': attribute.products.all()
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
    template_name = 'dashboard/attribute_update.html'
    page_title = _('Attribute Update')
    
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
    else:
        form = ProductAttributeForm(instance=attribute)
    context = {
        'page_title': page_title,
        'form' : form,
        'brand': attribute
    }
    context.update(get_view_permissions(request.user))
    return render(request, template_name, context)


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
    paginator = Paginator(queryset, 10)
    try:
        list_set = paginator.page(page)
    except PageNotAnInteger:
        list_set = paginator.page(1)
    except EmptyPage:
        list_set = None
    context = {
        'page_title': page_title,
        'attribute_list': list_set
    }
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)


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

    queryset = models.Brand.objects.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, 10)
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
    paginator = Paginator(queryset, 10)
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
    paginator = Paginator(queryset, utils.PAGINATED_BY)
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
    context['report'] = json.dumps(analytics.report_orders_for_year())
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
    paginator = Paginator(queryset, utils.PAGINATED_BY)
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
    template_name = "dashboard/user_detail.html"
    page_title = "User Details - " + settings.SITE_NAME
    context['page_title'] = page_title
    context['user_instance'] = user
    context.update(get_view_permissions(request.user))
    context['can_delete'] = PermissionManager.user_can_delete_user(request.user)
    context['can_update'] = PermissionManager.user_can_change_user(request.user)
    return render(request,template_name, context)


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
    paginator = Paginator(queryset, utils.PAGINATED_BY)
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
        Brand.objects.filter(id__in=instance_list).delete()
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
            logger.info("Edit ServiceCategoryForm is not valid. Errors : %s", form.errors)
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
    paginator = Paginator(queryset, utils.PAGINATED_BY)
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
    paginator = Paginator(group_list, utils.PAGINATED_BY)
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
    paginator = Paginator(permission_list, utils.PAGINATED_BY)
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
    paginator = Paginator(queryset, utils.PAGINATED_BY)
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
    paginator = Paginator(queryset, utils.PAGINATED_BY)
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
    if request.method == 'POST':
        postdata = utils.get_postdata(request)
        form = CouponForm(postdata)
        if form.is_valid():
            coupon = form.save()
            messages.success(request, _('New Coupon created'))
            logger.info(f'New Coupon added by user \"{username}\"')
            return redirect(coupon)
        else:
            messages.error(request, _('Coupon not created'))
            logger.error(f'Error on creating new Coupon. Action requested by user \"{username}\"')
    else:
        form = CouponForm()
    context = {
        'page_title': page_title,
        'form' : form
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
        'coupon': coupon
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
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if request.method != "POST":
        raise SuspiciousOperation('Bad request. Expected POST request but received a GET')
    
    postdata = utils.get_postdata(request)
    id_list = postdata.getlist('coupons')

    if len(id_list):
        coupon_list = list(map(int, id_list))
        Coupon.objects.filter(id__in=coupon_list).delete()
        messages.success(request, f"Coupon \"{coupon_list}\" deleted")
        logger.info(f"Coupons \"{coupon_list}\" deleted by user {username}")
        
    else:
        messages.error(request, f"Coupons could not be deleted")
        logger.error(f"ID list invalid. Error : {id_list}")
    return redirect('dashboard:coupons')