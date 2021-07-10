from catalog.models import Category, Brand, Product, News, ProductType
from catalog import constants as CATALOG_CONSTANT, catalog_service
from django.utils import timezone

def catalog_context(request):

    context = {
        #'root_category_list': Category.objects.select_related().filter(parent=None, is_active=True).exclude(children=None),
        'root_category_list': catalog_service.find_children(root=None),
        'brand_list': catalog_service.get_brands(),
        'FILTER_CONFIG' : Product.CATALOGUE_FILTER_CONFIG,
        'news' : News.objects.filter(is_active=True, end_at__gt=timezone.now()).first(),
        'GENDER': CATALOG_CONSTANT.GENDER,
        'PRODUCT_TYPES': catalog_service.get_product_types()
    }
    return context