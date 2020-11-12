from catalog.models import Category, Brand, Product

def catalog_context(request):

    context = {
        'root_category_list': Category.objects.filter(parent=None),
        'brand_list': Brand.objects.all(),
        'FILTER_CONFIG' : Product.CATALOGUE_FILTER_CONFIG
    }
    return context