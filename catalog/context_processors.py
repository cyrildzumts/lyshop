from catalog.models import Category, Brand, Product, News, ProductType
from catalog import constants as CATALOG_CONSTANT
from django.utils import timezone

def catalog_context(request):

    context = {
        'root_category_list': Category.objects.filter(parent=None, is_active=True),
        'brand_list': Brand.objects.all(),
        'FILTER_CONFIG' : Product.CATALOGUE_FILTER_CONFIG,
        'news' : News.objects.filter(is_active=True, end_at__gt=timezone.now()).first(),
        'GENDER': CATALOG_CONSTANT.GENDER,
        'PRODUCT_TYPES': ProductType.objects.all()
    }
    return context