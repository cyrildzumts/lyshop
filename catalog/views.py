from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_protect
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.templatetags.static import static
from django.contrib.auth.models import User
from django.http import Http404
from django.http import HttpResponseRedirect
from django.http import HttpResponseBadRequest
from django.http import HttpResponse
from django.urls import reverse, resolve
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseForbidden
from django.contrib import messages
from django.db.models import F, Q, Count
from django.forms import formset_factory, modelformset_factory
from rest_framework.authtoken.models import Token
from accounts.forms import AccountCreationForm, UserCreationForm
from accounts.account_services import AccountService
from catalog.models import (
    Product, Brand, Category, ProductAttribute, ProductVariant, ProductImage, ProductType
)
from catalog.forms import (BrandForm, ProductAttributeForm, 
    ProductForm, ProductVariantForm, CategoryForm, ProductImageForm, AttributeForm, AddAttributeForm
)
from cart import cart_service
from cart.forms import AddCartForm
from core.filters import filters
from django.shortcuts import render
from django.views.generic import ListView, DetailView

from operator import itemgetter
from catalog import catalog_service, constants as Constants
from lyshop import utils, settings, conf as GLOBAL_CONF
import logging


logger = logging.getLogger(__name__)
# Create your views here.



class ProductListView(ListView):
    queryset = Product.objects.filter(is_active=True)
    context_object_name = GLOBAL_CONF.PRODUCT_LIST_CONTEXT_NAME
    template_name = GLOBAL_CONF.PRODUCT_LIST_TEMPLATE_NAME
    paginated_by = GLOBAL_CONF.PAGINATED_BY


class ProductDetailView(DetailView):
    model = Product
    pk_url_kwarg = GLOBAL_CONF.PK_ULR_KWARG
    context_object_name = GLOBAL_CONF.PRODUCT_DETAIL_CONTEXT_NAME
    template_name = GLOBAL_CONF.PRODUCT_DETAIL_TEMPLATE_NAME

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["product_variants"] = self.get_object().variants.all()
        return context
    


def catalog_home(request):
    template_name = GLOBAL_CONF.CATALOG_HOME_TEMPLATE_NAME
    recent_products = Product.objects.filter(is_active=True)[:GLOBAL_CONF.LATEST_QUERYSET_LIMIT]
    queryDict = request.GET.copy()
    field_filter = filters.Filter(Product, queryDict)
    queryset = field_filter.apply_filter().filter(is_active=True)
    selected_filters = field_filter.selected_filters
    context = {
        'page_title' : Constants.CATALOG_HOME_PAGE_TITLE,
        'product_list': recent_products,
        'type_list': ProductType.objects.all(),
        'queryset' : queryset,
        'GENDER' : Constants.GENDER,
        'SELECTED_FILTERS' : selected_filters,
        'OG_TITLE' : Constants.CATALOG_HOME_PAGE_TITLE,
        'OG_DESCRIPTION': settings.META_DESCRIPTION,
        'OG_IMAGE': static('assets/lyshop_banner.png'),
        'OG_URL': request.build_absolute_uri()
    }

    return render(request, template_name, context)


def category_detail(request, category_uuid=None):
    template_name = 'catalog/category_detail.html'
    if request.method != 'GET':
        raise HttpResponseBadRequest

    category = get_object_or_404(Category, category_uuid=category_uuid)
    subcats = category.get_children()
    filterquery = Q(category__category_uuid=category_uuid)
    subcatquery = Q(category__id__in=subcats.values_list('id'))
    

    queryDict = request.GET.copy()
    field_filter = filters.Filter(Product, queryDict)
    queryset = field_filter.apply_filter().filter(is_active=True)
    selected_filters = field_filter.selected_filters
    queryset = queryset.filter(filterquery | subcatquery)
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, GLOBAL_CONF.PAGINATED_BY)
    try:
        list_set = paginator.page(page)
    except PageNotAnInteger:
        list_set = paginator.page(1)
    except EmptyPage:
        list_set = None

    context = {
        'page_title': category.get_page_title(),
        'category' : category,
        'parent_category' : category.parent,
        'product_list': list_set,
        'type_list': ProductType.objects.all(),
        'parent_sub_category_list': Category.objects.filter(parent=category.parent),
        'subcategory_list': subcats,
        'GENDER' : Constants.GENDER,
        'SELECTED_FILTERS' : selected_filters,
        'OG_TITLE' : category.get_page_title(),
        'OG_DESCRIPTION': settings.META_DESCRIPTION,
        'OG_IMAGE': static('assets/lyshop_banner.png'),
        'OG_URL': request.build_absolute_uri()
    }
    return render(request,template_name, context)


def brand_detail(request, brand_uuid=None):
    template_name = 'catalog/brand_detail.html'
    if request.method != 'GET':
        raise HttpResponseBadRequest

    brand = get_object_or_404(Brand, brand_uuid=brand_uuid)
    queryset = Product.objects.filter(brand__brand_uuid=brand_uuid, is_active=True)
    page_title = _(brand.display_name)
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
        'brand' : brand,
        'product_list': list_set
    }
    return render(request,template_name, context)


def product_detail(request, product_uuid=None):
    template_name = 'catalog/product_detail.html'
    product = get_object_or_404(Product, product_uuid=product_uuid)
    page_title = product.display_name 
    if request.method == "POST":
        form = AddCartForm(utils.get_postdata(request))
        if form.is_valid():
            variant = get_object_or_404(ProductVariant, product_uuid=form.cleaned_data['variant_uuid'])
            item, cart = cart_service.add_to_cart(cart_service.get_cart(request.user), variant)
            if item:
                messages.success(request, message="Product added")
                logger.info("Product added")
            else:
                messages.success(request, message="Product not added")
                logger.info("Product not added")
        else:
                messages.success(request, message="Invalid form")
                logger.info(f"Product not added. Form is not valid : {form.errors} ")
                
    Product.objects.filter(product_uuid=product_uuid).update(view_count=F('view_count') + 1)
    images = ProductImage.objects.filter(product=product)
    common_attrs, selective_attrs = catalog_service.get_product_attributes(product.id)
    product_attrs = catalog_service.product_attributes(product.id)

    context = {
        'page_title': page_title,
        'product': product,
        'image_list': images,
        'common_attrs' : common_attrs,
        'selective_attrs' : selective_attrs,
        'product_attrs': product_attrs,
        'OG_TITLE' : page_title,
        'OG_DESCRIPTION': product.short_description,
        'OG_IMAGE': product.images.first().get_image_url(),
        'OG_URL': request.build_absolute_uri()
    }
    return render(request,template_name, context)

@login_required
def add_product_to_cart(request):
    cart, created = CartModel.objects.get_or_create(user=request.user)
    context = {
        'success': False
    }
    logger.debug("ajax-add-to-cart")
    utils.show_request(request)
    template_name = 'catalog/product_detail.html'
    page_title = _('Product Detail')
    if request.method == 'POST':
        postdata = request.POST.copy()
        logger.info("send as POST")
        form = AddCartForm(postdata)
        if form.is_valid():
            product = form.cleaned_data['product']
            result , cart = cart_service.add_to_cart(cart, product)
            if result:
                context['success'] = True
                context['status'] = True
                #return redirect(product.get_absolute_url())
        else:
            context['error'] = 'Form is invalid'
            context['status'] = False
            messages.error(request, message="Invalid Form")
            #if request.is_ajax():
            #   return JsonResponse(context,status=HTTPStatus.BAD_REQUEST)
            
    else:
        context['error'] = 'Bad Request'
        context['status'] = False
        return 


def product_variant_detail(request, variant_uuid=None):
    template_name = 'catalog/product_variant_detail.html'
    page_title = _('Product Variant Detail')
    
    if request.method != 'GET':
        raise HttpResponseBadRequest

    variant = get_object_or_404(ProductVariant, product_uuid=variant_uuid)
    Product.objects.filter(product_uuid=variant.product.product_uuid).update(view_count=F('view_count') + 1)
    images = ProductImage.objects.filter(product=variant.product)
    common_attrs, selective_attrs = catalog_service.get_product_variant_attrs(variant.product.id)
    attrs = variant.attributes.all()
    attrs_values = variant.attributes.values('name','display_name').annotate(count=Count('name'))
    filter_attrs = []
    selectable_attrs = []
    for e in attrs_values:
        if e['count'] > 1:
            selectable_attrs.append({'name': e['name'], 'display_name': e['display_name'], 'values': sorted([k.get('value') for k in attrs.filter(name=e['name']).values('value')])})
            filter_attrs.append(e['name'])

    context = {
        'page_title': page_title,
        'variant': variant,
        'product': variant.product,
        'image_list': images,
        'attribute_list': variant.attributes.exclude(name__in=filter_attrs).all(),
        'selectable_attrs': selectable_attrs,
        'common_attrs' : common_attrs,
        'selective_attrs' : selective_attrs
    }
    return render(request,template_name, context)


def product_image_detail(request, image_uuid=None):
    if request.method != 'GET':
        raise HttpResponseBadRequest
    context = {}
    image = get_object_or_404(ProductImage, image_uuid=image_uuid)

    template_name = "catalog/product_image_detail.html"
    page_title = "Product Image" + " - " + settings.SITE_NAME
    context['page_title'] = page_title
    context['image'] = image
    return render(request,template_name, context)

