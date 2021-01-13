from catalog.models import Category, Brand, Product, News
from django.utils import timezone

def catalog_context(request):

    context = {
        'root_category_list': Category.objects.filter(parent=None),
        'brand_list': Brand.objects.all(),
        'FILTER_CONFIG' : Product.CATALOGUE_FILTER_CONFIG,
        'news' : News.objects.filter(is_active=True, end_at__gt=timezone.now()).first()
    }
    return context