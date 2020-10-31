from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_protect
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied, SuspiciousOperation

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


from django.shortcuts import render
from django.views.generic import ListView, DetailView

from operator import itemgetter
from catalog import catalog_service
from lyshop import utils, settings, conf
import logging


logger = logging.getLogger(__name__)
# Create your views here.



class ProductListView(ListView):
    queryset = Product.objects.filter(is_active=True)
    context_object_name = conf.PRODUCT_LIST_CONTEXT_NAME
    template_name = conf.PRODUCT_LIST_TEMPLATE_NAME
    paginated_by = conf.PAGINATED_BY


class ProductDetailView(DetailView):
    model = Product
    pk_url_kwarg = conf.PK_ULR_KWARG
    context_object_name = conf.PRODUCT_DETAIL_CONTEXT_NAME
    template_name = conf.PRODUCT_DETAIL_TEMPLATE_NAME

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["product_variants"] = self.get_object().variants.all()
        return context
    


def catalog_home(request):
    page_title = _('Catalog Home')
    template_name = conf.CATALOG_HOME_TEMPLATE_NAME
    recent_products = Product.objects.all()[:conf.LATEST_QUERYSET_LIMIT]
    context = {
        'page_title' : page_title,
        'product_list': recent_products,
        'type_list': ProductType.objects.all()
    }

    return render(request, template_name, context)


def category_detail(request, category_uuid=None):
    template_name = 'catalog/category_detail.html'
    if request.method != 'GET':
        raise HttpResponseBadRequest

    category = get_object_or_404(Category, category_uuid=category_uuid)
    subcats = category.get_children()
    logger.info(f"Cat {category.display_name} children : {subcats.count()}")
    filterquery = Q(category__category_uuid=category_uuid)
    subcatquery = Q(category__id__in=subcats.values_list('id'))
    queryset = Product.objects.filter(filterquery | subcatquery)
    page_title = _(category.display_name)
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
        'category' : category,
        'parent_category' : category.parent,
        'product_list': list_set,
        'type_list': ProductType.objects.all(),
        'parent_sub_category_list': Category.objects.filter(parent=category.parent),
        'subcategory_list': subcats
    }
    return render(request,template_name, context)


def brand_detail(request, brand_uuid=None):
    template_name = 'catalog/brand_detail.html'
    if request.method != 'GET':
        raise HttpResponseBadRequest

    brand = get_object_or_404(Brand, brand_uuid=brand_uuid)
    queryset = Product.objects.filter(brand__brand_uuid=brand_uuid)
    page_title = _(brand.display_name)
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
        'brand' : brand,
        'product_list': list_set
    }
    return render(request,template_name, context)


def product_detail(request, product_uuid=None):
    template_name = 'catalog/product_detail.html'
    page_title = _('Product Detail')
    
    if request.method != 'GET':
        raise HttpResponseBadRequest

    product = get_object_or_404(Product, product_uuid=product_uuid)
    Product.objects.filter(product_uuid=product_uuid).update(view_count=F('view_count') + 1)
    images = ProductImage.objects.filter(product=product)
    common_attrs, selective_attrs = catalog_service.get_product_attributes(product.id)
    product_attrs = catalog_service.product_attributes(product.id)
    utils.show_dict_contents(product_attrs, f"Product Attributes for {product.display_name}")
    context = {
        'page_title': page_title,
        'product': product,
        'image_list': images,
        'common_attrs' : common_attrs,
        'selective_attrs' : selective_attrs,
        'product_attrs': product_attrs
    }
    return render(request,template_name, context)



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

