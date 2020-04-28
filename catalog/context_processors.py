from catalog.models import Category, Brand

def catalog_context(request):

    context = {
        'root_category_list': Category.objects.filter(parent=None),
        'brand_list': Brand.objects.all()
    }
    return context