from django.shortcuts import render, get_object_or_404
from django.db.models import F, Q, Sum, Count
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.utils import timezone
from django.forms import formset_factory, modelformset_factory

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
    product = get_object_or_404(Product, product_uuid=product_uuid, sold_by=request.user)
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
    context['brand_list'] = Brand.objects.all()
    context['category_list'] = Category.objects.all()
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

    product = get_object_or_404(Product, product_uuid=product_uuid, sold_by=request.user)
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
        Product.objects.filter(id__in=product_id_list, sold_by=request.user).delete()
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
def product_variant_create(request, product_uuid=None):
    username = request.user.username
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    template_name = 'vendors/product_variant_create.html'
    page_title = _('New Product Variant')
    
    form = None
    product = get_object_or_404(Product, product_uuid=product_uuid, sold_by=request.user)
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
            return redirect('vendors:product-detail', product_uuid=product_uuid)
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
    context['attribute_types'] = Catalog_Constants.ATTRIBUTE_TYPE
    return render(request, template_name, context)

@login_required
def product_variant_detail(request, variant_uuid=None):
    username = request.user.username
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    template_name = 'vendors/product_variant_detail.html'
    page_title = _('Product Variant Detail')
    attr_types = [v for k,v in Catalog_Constants.ATTRIBUTE_TYPE]
    variant = get_object_or_404(ProductVariant, product_uuid=variant_uuid, product__sold_by=request.user)
    product = variant.product
    attribute_formset = modelformset_factory(ProductAttribute, form=ProductAttributeForm, extra=4, max_num=5)
    attribute_list = variant.attributes.all()
    available_attribute_list = ProductAttribute.objects.exclude(id__in=attribute_list.values_list('id'))
    context = {
        'page_title': page_title,
        'product': product,
        'variant': variant,
        'attr_types': json.dumps(attr_types),
        'attribute_types' : Catalog_Constants.ATTRIBUTE_TYPE,
        'attribute_list' : attribute_list,
        'available_attribute_list' : available_attribute_list,
        'attribute_formset': attribute_formset(queryset=ProductAttribute.objects.none())
    }
    return render(request,template_name, context)

@login_required
def product_variant_update(request, variant_uuid=None):
    username = request.user.username
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    template_name = 'vendors/product_variant_update.html'
    page_title = _('Product Variant Update')
    
    form = None
    username = request.user.username
    variant = get_object_or_404(ProductVariant, product_uuid=variant_uuid, product__sold_by=request.user)
    product = variant.product
    attribute_formset = modelformset_factory(ProductAttribute, form=ProductAttributeForm, extra=4, max_num=5)
    if request.method == 'POST':
        postdata = utils.get_postdata(request)
        form = ProductVariantForm(postdata, instance=variant)
        if form.is_valid():
            p_variant = form.save()
            messages.success(request, _('Product variant updated'))
            logger.info(f'Product variant updated by user \"{username}\"')
            return redirect('vendors:product-variant-detail', variant_uuid=variant_uuid)
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
    return render(request, template_name, context)

@login_required
def product_variant_delete(request, variant_uuid=None):
    username = request.user.username
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if request.method != "POST":
        logger.warning(f"Delete request refused. User {request.user.username} trying to delete a product variant {variant_uuid} in non POST request")
        logger.warning(f"request method used for the Delete : \"{request.method}\"")
        raise SuspiciousOperation('Bad request')

    product_variant = get_object_or_404(ProductVariant, product_uuid=variant_uuid, product__sold_by=request.user)
    product = product_variant.product
    ProductVariant.objects.filter(pk=product_variant.pk).delete()
    logger.info(f'Product Variant \"{product_variant.display_name}\" deleted by user \"{request.user.username}\"')
    messages.success(request, _('Product variant deleted'))
    return redirect(product.get_vendor_url())

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

