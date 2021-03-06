from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import F, Q, Sum, Count
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.utils import timezone
from django.forms import formset_factory, modelformset_factory
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseForbidden
from django.contrib import messages
from catalog.models import Product, ProductVariant, Brand, Category, ProductTypeAttribute, ProductImage, ProductType, ProductAttribute
from catalog.forms import (BrandForm, ProductAttributeForm, 
    ProductForm, ProductVariantForm, CategoryForm, ProductImageForm, AttributeForm, AddAttributeForm, BrandForm,
    DeleteAttributeForm, CategoriesDeleteForm, ProductTypeForm, ProductTypeAttributeForm
)
from catalog import constants as Catalog_Constants
from accounts.models import Account
from cart.models import Coupon
from cart.forms import CouponForm
from orders.forms import OrderItemUpdateForm
from orders.models import Order, OrderItem
from orders import commons as Order_Constants
from core.filters import filters
from core.resources import ui_strings as CORE_STRINGS
from lyshop import utils, settings, conf as GLOBAL_CONF
from vendors import vendors_service
from vendors import constants as VENDORS_CONTANTS
from shipment import shipment_service
from vendors.models import Balance, BalanceHistory, VendorPayment, VendorPaymentHistory, SoldProduct
from payment.models import Payment
import logging
import json

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
        'product_count': product_count,
        'content_title' : CORE_STRINGS.DASHBOARD_VENDOR_HOME_TITLE
    }
    context.update(VENDORS_CONTANTS.DASHBOARD_PRODUCT_CONTEXT)
    return render(request, template_name, context)




@login_required
def brands(request):
    username = request.user.username
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    template_name = 'vendors/brand_list.html'
    page_title = _('Brands')
    if request.method != 'GET':
        return HttpResponseBadRequest('Bad request')

    queryset = Brand.objects.all().order_by('-created_at')
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
        'brand_list': list_set,
        'content_title': CORE_STRINGS.DASHBOARD_BRANDS_TITLE
    }
    context.update(VENDORS_CONTANTS.DASHBOARD_BRAND_CONTEXT)
    return render(request,template_name, context)

@login_required
def brand_create(request):
    username = request.user.username
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    template_name = 'vendors/brand_create.html'
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
            return redirect('vendors:brands')
        else:
            messages.error(request, _('Brand not created'))
            logger.error(f'Error on creating new Brand. Action requested by user \"{username}\"')
    else:
        form = BrandForm()
    context = {
        'page_title': page_title,
        'form' : form,
        'content_title': CORE_STRINGS.DASHBOARD_BRANDS_TITLE
    }
    context.update(VENDORS_CONTANTS.DASHBOARD_BRAND_CONTEXT)
    return render(request, template_name, context)

@login_required
def brand_detail(request, brand_uuid=None):
    username = request.user.username
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    template_name = 'vendors/brand_detail.html'
    page_title = _('Brand Detail')
    
    if request.method != "GET":
        raise SuspiciousOperation('Bad request')

    brand = get_object_or_404(Brand, brand_uuid=brand_uuid)
    product_list = Product.objects.filter(brand=brand, sold_by=request.user)
    context = {
        'page_title': page_title,
        'product_list': product_list,
        'brand': brand,
        'content_title': CORE_STRINGS.DASHBOARD_BRAND_TITLE
    }
    context.update(VENDORS_CONTANTS.DASHBOARD_BRAND_CONTEXT)
    return render(request,template_name, context)

@login_required
def brand_update(request, brand_uuid=None):
    username = request.user.username
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    template_name = 'vendors/brand_update.html'
    page_title = _('Brand Update')
    
    form = None
    username = request.user.username
    brand = get_object_or_404(Brand, brand_uuid=brand_uuid)
    if request.method == 'POST':
        postdata = utils.get_postdata(request)
        form = BrandForm(postdata, instance=brand)
        if form.is_valid():
            brand = form.save()
            messages.success(request, _('Brand updated'))
            logger.info(f'Brand updated by user \"{username}\"')
            return redirect('vendors:brand-detail', brand_uuid=brand_uuid)
        else:
            messages.error(request, _('Brand not updated'))
            logger.error(f'Error on updated Brand. Action requested by user \"{username}\"')
    else:
        form = BrandForm(instance=brand)
    context = {
        'page_title': page_title,
        'form' : form,
        'brand': brand,
        'content_title' : CORE_STRINGS.DASHBOARD_BRAND_UPDATE_TITLE
    }
    context.update(VENDORS_CONTANTS.DASHBOARD_BRAND_CONTEXT)
    return render(request, template_name, context)


@login_required
def brand_delete(request, brand_uuid=None):
    username = request.user.username
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if request.method != "POST":
        raise SuspiciousOperation('Bad request')

    brand = get_object_or_404(Brand, brand_uuid=brand_uuid)
    brand_name = brand.name
    brand.delete()
    logger.info(f'Brand \"{brand_name}\" deleted by user \"{request.user.username}\"')
    messages.success(request, _('Brand deleted'))
    return redirect('vendors:brands')


@login_required
def brands_delete(request):
    username = request.user.username
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
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
    return redirect('vendors:brands')


@login_required
def brand_products(request, brand_uuid=None):
    username = request.user.username
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    template_name = 'vendors/brand_product_list.html'
    page_title = _('Brand Products')
    
    if request.method != 'GET':
        return HttpResponseBadRequest('Bad request')

    brand = get_object_or_404(Brand, brand_uuid=brand_uuid)
    queryset = Product.objects.filter(brand=brand, sold_by=request.user)
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
        'brand': brand,
        'content_title': CORE_STRINGS.DASHBOARD_BRAND_PRODUCTS_TITLE
    }
    context.update(VENDORS_CONTANTS.DASHBOARD_BRAND_CONTEXT)
    return render(request,template_name, context)


@login_required
def brand_product_detail(request, brand_uuid=None, product_uuid=None):
    username = request.user.username
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    template_name = 'vendors/brand_product_detail.html'
    page_title = _('Product Detail')
    

    product = get_object_or_404(Product, brand__brand_uuid=brand_uuid, product_uuid=product_uuid, sold_by=request.user)
    context = {
        'page_title': page_title,
        'product': product
    }
    context.update(VENDORS_CONTANTS.DASHBOARD_BRAND_CONTEXT)
    return render(request,template_name, context)





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
        'content_title': CORE_STRINGS.DASHBOARD_PRODUCTS_TITLE
    }

    #queryset = Product.objects.filter(is_active=True, sold_by=request.user).order_by('-created_at')
    #queryset = Product.objects.order_by('-created_at')
    queryDict = request.GET.copy()
    field_filter = filters.Filter(Product, queryDict)
    queryset = field_filter.apply_filter().filter(sold_by=request.user)
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
    context.update(VENDORS_CONTANTS.DASHBOARD_PRODUCT_CONTEXT)
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
        'image_list': images,
        'content_title': CORE_STRINGS.DASHBOARD_PRODUCT_TITLE
    }
    context.update(VENDORS_CONTANTS.DASHBOARD_PRODUCT_CONTEXT)
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
        'content_title' : CORE_STRINGS.DASHBOARD_PRODUCT_UPDATE_TITLE,
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
    context['brand_list'] = Brand.objects.filter(is_active=True)
    context['category_list'] = Category.objects.filter(is_active=True)
    context['product_type_list'] = ProductType.objects.all()
    context['GENDER'] = Catalog_Constants.GENDER
    context['DESCRIPTION_MAX_SIZE'] = Catalog_Constants.DESCRIPTION_MAX_SIZE
    context['SHORT_DESCRIPTION_MAX_SIZE'] = Catalog_Constants.SHORT_DESCRIPTION_MAX_SIZE
    context.update(VENDORS_CONTANTS.DASHBOARD_PRODUCT_CONTEXT)
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
        'content_title': CORE_STRINGS.DASHBOARD_PRODUCT_CREATE_TITLE
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
    context['brand_list'] = Brand.objects.filter(is_active=True)
    context['category_list'] = Category.objects.filter(is_active=True)
    context['product_type_list'] = ProductType.objects.all()
    context['GENDER'] = Catalog_Constants.GENDER
    context['DESCRIPTION_MAX_SIZE'] = Catalog_Constants.DESCRIPTION_MAX_SIZE
    context['SHORT_DESCRIPTION_MAX_SIZE'] = Catalog_Constants.SHORT_DESCRIPTION_MAX_SIZE
    context.update(VENDORS_CONTANTS.DASHBOARD_PRODUCT_CONTEXT)
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
        'attribute_formset': attribute_formset(queryset=ProductAttribute.objects.none()),
        'content_title' : CORE_STRINGS.DASHBOARD_PRODUCT_VARIANTE_CREATE_TITLE,
    }
    context['attribute_formset'] = attribute_formset
    context['ATTRIBUTE_TYPE'] = Catalog_Constants.ATTRIBUTE_TYPE
    context.update(VENDORS_CONTANTS.DASHBOARD_PRODUCT_CONTEXT)
    return render(request, template_name, context)

@login_required
def product_variant_detail(request, variant_uuid=None):
    username = request.user.username
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    template_name = 'vendors/product_variant_detail.html'
    page_title = _('Product Variant Detail')
    attr_types = [k for k,v in Catalog_Constants.ATTRIBUTE_TYPE]
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
        'ATTRIBUTE_TYPE' : Catalog_Constants.ATTRIBUTE_TYPE,
        'attribute_list' : attribute_list,
        'available_attribute_list' : available_attribute_list,
        'attribute_formset': attribute_formset(queryset=ProductAttribute.objects.none()),
        'content_title' : CORE_STRINGS.DASHBOARD_PRODUCT_VARIANTE_TITLE,
    }
    context.update(VENDORS_CONTANTS.DASHBOARD_PRODUCT_CONTEXT)
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
        'ATTRIBUTE_TYPE': Catalog_Constants.ATTRIBUTE_TYPE,
        'content_title' : CORE_STRINGS.DASHBOARD_PRODUCT_VARIANTE_UPDATE_TITLE,
    }
    context.update(VENDORS_CONTANTS.DASHBOARD_PRODUCT_CONTEXT)
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
def product_image_create(request, product_uuid=None):
    username = request.user.username
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    context = {
        'content_title' : CORE_STRINGS.DASHBOARD_PRODUCT_IMAGE_CREATE_TITLE,
    }    
    template_name = "vendors/product_image_create.html"
    page_title = "New Product Image" + " - " + settings.SITE_NAME
    context['page_title'] = page_title
    product = get_object_or_404(Product, product_uuid=product_uuid, sold_by=request.user)
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
                return JsonResponse({'status': 'OK', 'message' : _('Image(s)  uploaded')})
            return redirect(product.get_vendor_url())
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
    context.update(VENDORS_CONTANTS.DASHBOARD_PRODUCT_CONTEXT)
    return render(request,template_name, context)

@login_required
def product_image_detail(request, image_uuid=None):
    username = request.user.username
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    context = {
        'content_title' : CORE_STRINGS.DASHBOARD_PRODUCT_IMAGE_TITLE
    }
    image = get_object_or_404(ProductImage, image_uuid=image_uuid, product__sold_by=request.user)

    template_name = "vendors/product_image_detail.html"
    page_title = "Product Image" + " - " + settings.SITE_NAME
    context['page_title'] = page_title
    context['image'] = image
    context.update(VENDORS_CONTANTS.DASHBOARD_PRODUCT_CONTEXT)
    return render(request,template_name, context)

@login_required
def product_image_delete(request, image_uuid=None):
    username = request.user.username
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    
    '''
    if request.method != "POST":
        raise SuspiciousOperation('Bad request')
    '''
    context = {}

    p_image = get_object_or_404(ProductImage, image_uuid=image_uuid, product__sold_by=request.user)
    product = p_image.product
    p_image.delete_image_file()
    ProductImage.objects.filter(pk=p_image.pk).delete()
    messages.success(request, _("Image removed"))
    return redirect(product.get_vendor_url())

@login_required
def product_image_update(request, image_uuid=None):
    username = request.user.username
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    page_title = "Edit Product Image" + ' - ' + settings.SITE_NAME
    template_name = "vendors/product_image_update.html"
    image = get_object_or_404(ProductImage, image_uuid=image_uuid, product__sold_by=request.user)
    if request.method == "POST":
        form = ProductImageForm(request.POST, request.FILES, instance=image)
        if form.is_valid():
            logger.info("ProductImageForm is valid")
            form.save()
            return redirect(image.product.get_vendor_url())
        else:
            logger.info("Edit image form is not valid. Errors : %s", form.errors)
            logger.info("Form clean data : %s", form.cleaned_data)
    elif request.method == 'GET':
        form = ProductImageForm(instance=image)
    context = {
            'page_title': page_title,
            'template_name': template_name,
            'image'  : image,
            'form': form,
            'content_title' : CORE_STRINGS.DASHBOARD_PRODUCT_IMAGE_UPDATE_TITLE
        }
    
    return render(request, template_name,context )

@login_required
def product_images(request, product_uuid):
    username = request.user.username
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    context = {}
    product = get_object_or_404(Product, product_uuid=product_uuid, sold_by=request.user)
    queryset = ProductImage.objects.filter(product=product).order_by('-created_at')
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, GLOBAL_CONF.PAGINATED_BY)
    try:
        list_set = paginator.page(page)
    except PageNotAnInteger:
        list_set = paginator.page(1)
    except EmptyPage:
        list_set = None
    template_name = "vendors/product_images_list.html"
    page_title = "Product Images" + " - " + settings.SITE_NAME
    context['page_title'] = page_title
    context['image_list'] = list_set
    context['product'] = product
    context.update(VENDORS_CONTANTS.DASHBOARD_PRODUCT_CONTEXT)
    return render(request,template_name, context)



@login_required
def add_attributes(request, variant_uuid):
    username = request.user.username
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    form = None
    username = request.user.username
    variant = get_object_or_404(ProductVariant, product_uuid=variant_uuid, product__sold_by=request.user)
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
            
    return redirect('vendors:product-variant-detail', variant_uuid=variant_uuid)


@login_required
def remove_attributes(request, variant_uuid):
    username = request.user.username
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    form = None
    username = request.user.username
    variant = get_object_or_404(ProductVariant, product_uuid=variant_uuid, product__sold_by=request.user)
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
            
    return redirect('vendors:product-variant-detail', variant_uuid=variant_uuid)


@login_required
def attribute_create(request, variant_uuid):
    username = request.user.username
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    template_name = 'vendors/attribute_create.html'
    page_title = _('New Attribute')
    
    form = None
    username = request.user.username
    variant = get_object_or_404(ProductVariant, product_uuid=variant_uuid, product__sold_by=request.user)
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
            return redirect('vendors:product-variant-detail', variant_uuid=variant_uuid)
        else:
            messages.error(request, _('Product variant not created'))
            logger.error(f'Error on creating new product variant. Action requested by user \"{username}\"')
            logger.error(formset.errors)
            return redirect('vendors:product-variant-detail', variant_uuid=variant_uuid)
    else:
        form = ProductVariantForm()
    context = {
        'page_title': page_title,
        'formset' : attribute_formset(),
        'variant' : variant,
        'content_title' : CORE_STRINGS.DASHBOARD_ATTRIBUTE_CREATE_TITLE
    }
    context['attribute_formset'] = attribute_formset
    context['ATTRIBUTE_TYPE'] = Catalog_Constants.ATTRIBUTE_TYPE
    context.update(VENDORS_CONTANTS.DASHBOARD_ATTRIBUTES_CONTEXT)
    return render(request, template_name, context)

@login_required
def attribute_delete(request, attribute_uuid=None):
    username = request.user.username
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if request.method != "POST":
        raise SuspiciousOperation('Bad request')

    attribute = get_object_or_404(ProductAttribute, attribute_uuid=attribute_uuid)
    ProductAttribute.objects.filter(id=attribute.id).delete()
    logger.info(f'Attribute \"{attribute.name}\" - value \"{attribute.value}\"  removed  by user \"{request.user.username}\"')
    messages.success(request, _('Product deleted'))
    return redirect('vendors:attributes' )


@login_required
def delete_attributes(request):
    username = request.user.username
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
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
            
    return redirect('vendors:attributes')


@login_required
def attribute_detail(request, attribute_uuid):
    username = request.user.username
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    template_name = 'vendors/attribute_detail.html'
    page_title = _('Attribute')
    
    attribute = get_object_or_404(ProductAttribute, attribute_uuid=attribute_uuid)
    context = {
        'page_title': page_title,
        'attribute' : attribute,
        'product_list': attribute.products.filter(product__sold_by=request.user),
        'content_title' : CORE_STRINGS.DASHBOARD_ATTRIBUTE_TITLE
    }
    context.update(VENDORS_CONTANTS.DASHBOARD_ATTRIBUTES_CONTEXT)
    return render(request,template_name, context)

@login_required
def attribute_update(request, attribute_uuid=None):
    username = request.user.username
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    template_name = 'vendors/attribute_update.html'
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
            return redirect(attribute.get_vendor_url())
        else:
            messages.error(request, _('Attribute not updated'))
            logger.error(f'Error on updated Attribute. Action requested by user \"{username}\"')
    else:
        form = ProductAttributeForm(instance=attribute)
    context = {
        'page_title': page_title,
        'form' : form,
        'brand': attribute,
        'content_title' : CORE_STRINGS.DASHBOARD_ATTRIBUTE_UPDATE_TITLE
    }
    context.update(VENDORS_CONTANTS.DASHBOARD_ATTRIBUTES_CONTEXT)
    return render(request, template_name, context)


@login_required
def attributes(request):
    username = request.user.username
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    template_name = 'vendors/attribute_list.html'
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
        'content_title' : CORE_STRINGS.DASHBOARD_ATTRIBUTES_TITLE
    }
    context.update(VENDORS_CONTANTS.DASHBOARD_ATTRIBUTES_CONTEXT)
    return render(request,template_name, context)





@login_required
def coupons(request):
    username = request.user.username
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    context = {
        'content_title' : CORE_STRINGS.DASHBOARD_COUPONS_TITLE
    }
    queryset = Coupon.objects.filter(seller=request.user).order_by('-created_at')
    template_name = "vendors/coupon_list.html"
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
    context.update(VENDORS_CONTANTS.DASHBOARD_COUPON_CONTEXT)
    return render(request,template_name, context)


@login_required
def coupon_detail(request, coupon_uuid=None):
    username = request.user.username
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    context = {
        'content_title' : CORE_STRINGS.DASHBOARD_COUPON_TITLE
    }
    coupon = get_object_or_404(Coupon, coupon_uuid=coupon_uuid, seller=request.user)
    template_name = "vendors/coupon_detail.html"
    page_title = "Coupon" + " - " + settings.SITE_NAME
    context['page_title'] = page_title
    context['coupon'] = coupon
    context.update(VENDORS_CONTANTS.DASHBOARD_COUPON_CONTEXT)
    return render(request,template_name, context)


@login_required
def coupon_create(request):
    username = request.user.username
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    template_name = 'vendors/coupon_create.html'
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
            return redirect(coupon.get_vendor_url())
        else:
            messages.error(request, _('Coupon not created'))
            logger.error(f'Error on creating new Coupon. Action requested by user \"{username}\"')
    else:
        form = CouponForm()
    context = {
        'page_title': page_title,
        'form' : form,
        'content_title' : CORE_STRINGS.DASHBOARD_COUPON_CREATE_TITLE
    }
    context.update(VENDORS_CONTANTS.DASHBOARD_COUPON_CONTEXT)
    return render(request, template_name, context)


@login_required
def coupon_update(request, coupon_uuid=None):
    username = request.user.username
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    template_name = 'vendors/coupon_update.html'
    page_title = _('Coupon Update')
    
    form = None
    username = request.user.username
    coupon = get_object_or_404(Coupon, coupon_uuid=coupon_uuid, seller=request.user)
    

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
            return redirect(coupon.get_vendor_url())
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
        'content_title' : CORE_STRINGS.DASHBOARD_COUPON_UPDATE_TITLE
    }
    context.update(VENDORS_CONTANTS.DASHBOARD_COUPON_CONTEXT)
    return render(request, template_name, context)


@login_required
def coupon_delete(request, coupon_uuid=None):
    username = request.user.username
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied


    if request.method != "POST":
        raise SuspiciousOperation('Bad request')

    coupon = get_object_or_404(Coupon, coupon_uuid=coupon_uuid, seller=request.user)
    coupon_name = coupon.name
    coupon.delete()
    logger.info(f'Coupon \"{coupon_name}\" deleted by user \"{request.user.username}\"')
    messages.success(request, _('Coupon deleted'))
    return redirect('vendors:coupons')



@login_required
def coupons_delete(request):
    username = request.user.username
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if request.method != "POST":
        raise SuspiciousOperation('Bad request')
    postdata = utils.get_postdata(request)
    id_list = postdata.getlist('coupons')

    if len(id_list):
        coupon_list = list(map(int, id_list))
        Coupon.objects.filter(id__in=coupon_list, seller=request.user).delete()
        messages.success(request, f"Coupons \"{coupon_list}\" deleted")
        logger.info(f"Coupon \"{coupon_list}\" deleted by user {username}")
        
    else:
        messages.error(request, f"Coupons  could not be deleted")
        logger.error(f"Coupon Delete : ID list invalid. Error : {id_list}")
    return redirect('vendors:coupons')





@login_required
def product_types(request):
    username = request.user.username
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied


    template_name = 'vendors/product_type_list.html'
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
        'product_type_list': list_set,
        'content_title' : CORE_STRINGS.DASHBOARD_PRODUCT_TYPES_TITLE
    }
    context.update(VENDORS_CONTANTS.DASHBOARD_PRODUCT_TYPES_CONTEXT)
    return render(request,template_name, context)


@login_required
def product_type_create(request):
    username = request.user.username
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    template_name = 'vendors/product_type_create.html'
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
            return redirect('vendors:product-types')
        else:
            messages.error(request, _('ProductType not created'))
            logger.error(f'Error on creating new ProductType. Action requested by user \"{username}\"')
            logger.error(form.errors.items())
    else:
        form = ProductTypeForm()
    context = {
        'page_title': page_title,
        'type_attributes' : ProductTypeAttribute.objects.all(),
        'form' : form,
        'content_title' : CORE_STRINGS.DASHBOARD_PRODUCT_TYPE_CREATE_TITLE
    }
    context.update(VENDORS_CONTANTS.DASHBOARD_PRODUCT_TYPES_CONTEXT)
    return render(request, template_name, context)

@login_required
def product_type_detail(request, type_uuid=None):
    username = request.user.username
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    template_name = 'vendors/product_type_detail.html'
    page_title = _('ProductType Detail')
    
    if request.method != "GET":
        raise SuspiciousOperation('Bad request')

    product_type = get_object_or_404(ProductType, type_uuid=type_uuid)
    product_list = Product.objects.filter(product_type=product_type, sold_by=request.user)
    context = {
        'page_title': page_title,
        'product_list': product_list,
        'product_type': product_type,
        'ATTRIBUTE_TYPE': Catalog_Constants.ATTRIBUTE_TYPE,
        'content_title' : CORE_STRINGS.DASHBOARD_PRODUCT_TYPE_TITLE
    }
    context.update(VENDORS_CONTANTS.DASHBOARD_PRODUCT_TYPES_CONTEXT)
    return render(request,template_name, context)

@login_required
def product_type_update(request, type_uuid=None):
    username = request.user.username
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    template_name = 'vendors/product_type_update.html'
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
            return redirect('vendors:product-type-detail', type_uuid=type_uuid)
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
        'type_attributes' : ProductTypeAttribute.objects.exclude(id__in=product_type.type_attributes.all()),
        'content_title' : CORE_STRINGS.DASHBOARD_PRODUCT_TYPE_UPDATE_TITLE
    }
    context.update(VENDORS_CONTANTS.DASHBOARD_PRODUCT_TYPES_CONTEXT)
    return render(request, template_name, context)


@login_required
def product_type_delete(request, type_uuid=None):
    username = request.user.username
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied


    if request.method != "POST":
        raise SuspiciousOperation('Bad request')

    product_type = get_object_or_404(models.ProductType, type_uuid=type_uuid)
    product_type_name = product_type.name
    product_type.delete()
    logger.info(f'ProductType \"{product_type_name}\" deleted by user \"{request.user.username}\"')
    messages.success(request, _('ProductType deleted'))
    return redirect('vendors:product-types')


@login_required
def product_types_delete(request):
    username = request.user.username
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
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
    return redirect('vendors:product-types')


@login_required
def product_type_products(request, type_uuid=None):
    username = request.user.username
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    template_name = 'vendors/type_product_list.html'
    page_title = _('Product Type Products')
    
    if request.method != 'GET':
        return HttpResponseBadRequest('Bad request')

    product_type = get_object_or_404(ProductType, type_uuid=type_uuid)
    queryset = Product.objects.filter(product_type=product_type, sold_by=request.user)
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
        'product_type': product_type,
        'content_title' : CORE_STRINGS.DASHBOARD_PRODUCT_TYPE_PRODUCTS_TITLE
    }
    context.update(VENDORS_CONTANTS.DASHBOARD_PRODUCT_TYPES_CONTEXT)
    return render(request,template_name, context)

## PRODUCT TYPE ATTRIBUTES

@login_required
def product_type_attributes(request):
    username = request.user.username
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied


    template_name = 'vendors/product_type_attribute_list.html'
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
        'content_title' : CORE_STRINGS.DASHBOARD_TYPE_ATTRIBUTES_TITLE
    }
    context.update(VENDORS_CONTANTS.DASHBOARD_TYPES_ATTRIBUTE_CONTEXT)
    return render(request,template_name, context)


@login_required
def product_type_attribute_create(request):
    username = request.user.username
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    template_name = 'vendors/product_type_attribute_create.html'
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
            return redirect('vendors:product-type-attributes')
        else:
            messages.error(request, _('ProductType not created'))
            logger.error(f'Error on creating new ProductType. Action requested by user \"{username}\"')
            logger.error(form.errors.items())
    else:
        form = ProductTypeAttributeForm()
    context = {
        'page_title': page_title,
        'ATTRIBUTE_TYPE': Catalog_Constants.ATTRIBUTE_TYPE,
        'form' : form,
        'content_title' : CORE_STRINGS.DASHBOARD_TYPE_ATTRIBUTE_CREATE_TITLE
    }
    context.update(VENDORS_CONTANTS.DASHBOARD_TYPE_ATTRIBUTE_CREATE_TITLE)
    return render(request, template_name, context)

@login_required
def product_type_attribute_detail(request, type_attribute_uuid=None):
    username = request.user.username
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    template_name = 'vendors/product_type_attribute_detail.html'
    page_title = _('ProductTypeAttribute Detail')
    
    if request.method != "GET":
        raise SuspiciousOperation('Bad request')

    type_attribute = get_object_or_404(ProductTypeAttribute, type_attribute_uuid=type_attribute_uuid)
    #product_list = Product.objects.filter(product_type=product_type)
    context = {
        'page_title': page_title,
        #'product_list': product_list,
        'ATTRIBUTE_TYPE': Catalog_Constants.ATTRIBUTE_TYPE,
        'type_attribute': type_attribute,
        'content_title' : CORE_STRINGS.DASHBOARD_TYPE_ATTRIBUTE_TITLE
    }
    context.update(VENDORS_CONTANTS.DASHBOARD_TYPES_ATTRIBUTE_CONTEXT)
    return render(request,template_name, context)

@login_required
def product_type_attribute_update(request, type_attribute_uuid=None):
    username = request.user.username
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    template_name = 'vendors/product_type_attribute_update.html'
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
            return redirect('vendors:product-type-attributes')
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
        'type_attribute': type_attribute,
        'content_title' : CORE_STRINGS.DASHBOARD_TYPE_ATTRIBUTE_UPDATE_TITLE
    }
    context.update(VENDORS_CONTANTS.DASHBOARD_TYPES_ATTRIBUTE_CONTEXT)
    return render(request, template_name, context)


@login_required
def product_type_attribute_delete(request, type_attribute_uuid=None):
    username = request.user.username
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied


    if request.method != "POST":
        raise SuspiciousOperation('Bad request')

    product_type = get_object_or_404(ProductTypeAttribute, type_attribute_uuid=type_attribute_uuid)
    product_type_name = product_type.name
    product_type.delete()
    logger.info(f'ProductTypeAttribute \"{product_type_name}\" deleted by user \"{request.user.username}\"')
    messages.success(request, _('ProductTypeAttribute deleted'))
    return redirect('vendors:product-type-attributes')


@login_required
def product_type_attributes_delete(request):
    username = request.user.username
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
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
    return redirect('vendors:product-type-attributes')




@login_required
def sold_product_list(request):
    username = request.user.username
    
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    template_name = 'vendors/sold_product_list.html'
    page_title = _('Products')
    context = {
        'page_title': page_title,
        'content_title' : CORE_STRINGS.DASHBOARD_SOLD_PRODUCTS_TITLE
    }

    queryset = SoldProduct.objects.filter(seller=request.user).order_by('-created_at')
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
    context.update(VENDORS_CONTANTS.DASHBOARD_SOLD_PRODUCT_CONTEXT)
    return render(request,template_name, context)


@login_required
def sold_product_detail(request, product_uuid=None):
    template_name = 'vendors/sold_product_detail.html'
    username = request.user.username
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    page_title = _('Product Detail')
    
    sold_product = get_object_or_404(SoldProduct, product_uuid=product_uuid, seller=request.user)
    images = ProductImage.objects.filter(product=sold_product.product.product)
    context = {
        'page_title': page_title,
        'sold_product': sold_product,
        'product' : sold_product.product.product,
        'variant' : sold_product.product,
        'attribute_list': sold_product.product.attributes.all(),
        'image_list': images,
        'content_title' : CORE_STRINGS.DASHBOARD_SOLD_PRODUCT_TITLE
    }
    context.update(VENDORS_CONTANTS.DASHBOARD_SOLD_PRODUCT_CONTEXT)
    return render(request,template_name, context)



@login_required
def sold_product_delete(request, product_uuid=None):
    username = request.user.username
    
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if request.method != "POST":
        raise SuspiciousOperation('Bad request')

    product = get_object_or_404(SoldProduct, product_uuid=product_uuid, product__product__sold_by=request.user)
    p_name = product.product.name
    SoldProduct.objects.filter(pk=product.pk).delete()
    logger.info(f'SoldProduct \"{p_name}\" deleted by user \"{request.user.username}\"')
    messages.success(request, _('SoldProduct deleted'))
    return redirect('vendors:sold-products')



@login_required
def sold_products_delete(request):
    username = request.user.username
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
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
    return redirect('vendors:sold-products')



@login_required
def balance_history(request, balance_uuid):
    username = request.user.username
    
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied


    balance = get_object_or_404(Balance, balance_uuid=balance_uuid)
    queryset = BalanceHistory.objects.filter(balance__balance_uuid=balance_uuid)
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, GLOBAL_CONF.PAGINATED_BY)
    try:
        list_set = paginator.page(page)
    except PageNotAnInteger:
        list_set = paginator.page(1)
    except EmptyPage:
        list_set = None
    context = {
        'page_title' : _('Balance Histories'),
        'history_list':  list_set,
        'balance' : balance,
        'content_title': CORE_STRINGS.DASHBOARD_BALANCE_HYSTORIES_TITLE
    }
    template_name = 'vendors/balance_histories.html'
    return render(request, template_name, context)


@login_required
def balance_history_detail(request, history_uuid):
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

    context = {
        'content_title': CORE_STRINGS.DASHBOARD_PAYMENT_TITLE
    }
    payment = get_object_or_404(Payment, payment_uuid=payment_uuid)
    template_name = "vendors/payment_detail.html"
    page_title = "Payment Details - " + settings.SITE_NAME
    context['page_title'] = page_title
    context['payment'] = payment
    context['fee'] = payment.balance_amount - payment.amount
    context.update(VENDORS_CONTANTS.DASHBOARD_PAYMENTS_CONTEXT)
    return render(request,template_name, context)




@login_required
def payments(request):
    username = request.user.username

    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    context = {
        'content_title': CORE_STRINGS.DASHBOARD_PAYMENTS_TITLE
    }
    queryset = vendors_service.get_vendor_payments(request.user)
    template_name = "vendors/payment_list.html"
    page_title = "Payments - " + settings.SITE_NAME
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, GLOBAL_CONF.PAGINATED_BY)
    try:
        list_set = paginator.page(page)
    except PageNotAnInteger:
        list_set = paginator.page(1)
    except EmptyPage:
        list_set = None
    context['page_title'] = page_title
    context['payment_list'] = list_set
    context.update(VENDORS_CONTANTS.DASHBOARD_PAYMENTS_CONTEXT)
    return render(request,template_name, context)



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


@login_required
def orders(request):
    template_name = 'vendors/order_list.html'
    username = request.user.username
    
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    page_title = _('Order Item')
    order_items = OrderItem.objects.filter(product__product__sold_by=request.user).order_by('-created_at')
    page = request.GET.get('page', 1)
    paginator = Paginator(order_items, GLOBAL_CONF.PAGINATED_BY)
    try:
        list_set = paginator.page(page)
    except PageNotAnInteger:
        list_set = paginator.page(1)
    except EmptyPage:
        list_set = None

    context = {
        'page_title': page_title,
        'order_items' : list_set,
        'content_title': CORE_STRINGS.DASHBOARD_ORDERS_TITLE
    }
    context.update(VENDORS_CONTANTS.DASHBOARD_ORDERS_CONTEXT)
    return render(request,template_name, context)

@login_required
def order_item(request, order_uuid=None, item_uuid=None):
    template_name = 'vendors/order_item.html'
    username = request.user.username
    
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
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
        'content_title': CORE_STRINGS.DASHBOARD_ORDER_ITEM_TITLE
    }
    context.update(VENDORS_CONTANTS.DASHBOARD_ORDERS_CONTEXT)
    return render(request,template_name, context)

@login_required
def order_item_update(request, order_uuid=None, item_uuid=None):
    template_name = 'vendors/order_item_update.html'
    username = request.user.username
    
    if not vendors_service.is_vendor(request.user):
        logger.warning("Vendor Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    
    order = get_object_or_404(Order, order_uuid=order_uuid)
    item = get_object_or_404(OrderItem, item_uuid=item_uuid)
    page_title = _('Order Item Update')

    if request.method == 'POST':
        postdata = utils.get_postdata(request)
        form = OrderItemUpdateForm(postdata,instance=item)
        if form.is_valid():
            form.save()
            msg = f'Order Item {item} updated'
            messages.success(request, msg)
            logger.info(msg)
            return redirect(item.get_vendor_url())
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
        'form': OrderItemUpdateForm(instance=item),
        'content_title': CORE_STRINGS.DASHBOARD_ORDER_ITEM_UPDATE_TITLE
    }
    context.update(VENDORS_CONTANTS.DASHBOARD_ORDERS_CONTEXT)
    return render(request,template_name, context)