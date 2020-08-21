from django.shortcuts import render
from django.db.models import F, Q, Sum, Count
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from catalog.models import Product, ProductVariant, Brand, Category, ProductTypeAttribute, ProductImage, ProductType, ProductAttribute
from catalog.forms import (BrandForm, ProductAttributeForm, 
    ProductForm, ProductVariantForm, CategoryForm, ProductImageForm, AttributeForm, AddAttributeForm,
    DeleteAttributeForm, CategoriesDeleteForm, ProductTypeForm, ProductTypeAttributeForm
)
from catalog import constants as Catalog_Constants
from accounts.models import Account
from lyshop import settings
from vendors import vendors_service
from vendors.models import Balance, BalanceHistory, VendorPayment, VendorPaymentHistory, SoldProduct
import logging

logger = logging.getLogger(__name__)

# Create your views here.
@login_required
def vendor_home(request):

    username = request.user.username
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    template_name = "vendors/vendor_home.html"
    page_title = _("Vendor-Home")

    balance = None
    try:
        balance = Balance.objects.get(user=request.user)
    except ObjectDoesNotExist as e:
        logger.warn("Request User has no balance")
    
    sold_product_list = SoldProduct.objects.filter(seller=request.user).select_related()[:5]
    recent_products = Product.objects.filter(sold_by=request.user).order_by('-created_at')[:5]
    seller_product_queryset = ProductVariant.objects.filter(is_active=True, product__sold_by=request.user)
    product_count = seller_product_queryset.aggregate(product_count=Sum('quantity')).get('product_count', 0)
    number_sold_products = SoldProduct.objects.filter(seller=request.user).count()
    context = {
        'page_title' : page_title,
        'balance' : balance,
        'number_sold_products' : number_sold_products,
        'recent_sold_products': sold_product_list,
        'recent_products' : recent_products,
        'product_count': product_count
    }
    return render(request, template_name, context)


@login_required
def product_list(request):
    username = request.user.username
    
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    template_name = 'vendors/product_list.html'
    page_title = _('Products')
    context = {
        'page_title': page_title,
    }

    queryset = Product.objects.filter(is_active=True, sold_by=request.user).order_by('-created_at')
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

    return render(request,template_name, context)


@login_required
def product_detail(request, product_uuid=None):
    template_name = 'vendors/product_detail.html'
    username = request.user.username
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    page_title = _('Product Detail')
    

    product = get_object_or_404(Product, product_uuid=product_uuid, sold_by=request.user)
    images = ProductImage.objects.filter(product=product)
    variants = ProductVariant.objects.filter(product=product)
    context = {
        'page_title': page_title,
        'product': product,
        'variant_list': variants,
        'image_list': images
    }
    return render(request,template_name, context)

@login_required
def product_update(request, product_uuid=None):
    username = request.user.username
    
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    template_name = 'vendors/product_update.html'
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
            return redirect('vendors:product-detail', product_uuid=product_uuid)
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
    context['product_type_list'] = ProductType.objects.all()
    context['gender_list'] = Catalog_Constants.GENDER

    return render(request, template_name, context)

@login_required
def product_delete(request, product_uuid=None):
    username = request.user.username
    
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if request.method != "POST":
        raise SuspiciousOperation('Bad request')

    product = get_object_or_404(models.Product, product_uuid=product_uuid)
    p_name = product.name
    Product.objects.filter(pk=product.pk).delete()
    logger.info(f'Product \"{p_name}\" deleted by user \"{request.user.username}\"')
    messages.success(request, _('Product deleted'))
    return redirect('vendors:products')


@login_required
def products_delete(request):
    username = request.user.username
    
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
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
    return redirect('vendors:products')


@login_required
def product_create(request):
    username = request.user.username
    
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    template_name = 'vendors/product_create.html'
    page_title = _('New Product')
    
    context = {
        'page_title': page_title,
    }
    form = None
    
    if request.method == 'POST':
        postdata = utils.get_postdata(request)
        form = ProductForm(postdata)
        if form.is_valid():
            product = form.save()
            messages.success(request, _('New Product created'))
            logger.info(f'New product added by user \"{username}\"')
            return redirect('vendors:products')
        else:
            messages.error(request, _('Product not created'))
            logger.error(f'Error on creating new product. Action requested by user \"{username}\"')
    else:
        form = ProductForm()
    context['form'] = form
    context['brand_list'] = Brand.objects.all()
    context['category_list'] = Category.objects.all()
    context['user_list'] = User.objects.all()
    context['product_type_list'] = ProductType.objects.all()
    context['gender_list'] = Catalog_Constants.GENDER
    return render(request, template_name, context)



@login_required
def product_variant_list(request, product_uuid):
    username = request.user.username
    
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    template_name = 'vendors/product_variant_list.html'
    page_title = _('Products')
    context = {
        'page_title': page_title,
    }

    queryset = ProductVariant.objects.filter(is_active=True, product__sold_by=request.user ,product__product_uuid=product_uuid).order_by('-created_at')
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
    return render(request,template_name, context)



@login_required
def product_variant_detail(request, product_uuid):
    username = request.user.username
    
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

@login_required
def sold_product_list(request):
    username = request.user.username
    
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied




@login_required
def sold_product_detail(request, product_uuid):
    username = request.user.username
    
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

@login_required
def balance_history(request, balance_uuid):
    username = request.user.username
    
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied


@login_required
def balance_history_detail(request, history_uuid):
    username = request.user.username
    
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

@login_required
def vendor_payments(request):
    username = request.user.username
    
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied


@login_required
def payment_details(request, payment_uuid):
    username = request.user.username
    
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied


@login_required
def payment_history(request):
    username = request.user.username
    
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied


@login_required
def request_payment(request):
    username = request.user.username
    
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

