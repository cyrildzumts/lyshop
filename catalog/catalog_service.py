from os import EX_PROTOCOL
from cart.models import CartItem
from django.db.models import Q, Count
from django.core.cache import cache
from catalog.models import Category, Product, ProductAttribute, ProductVariant, ProductType, ProductTypeAttribute, News
from catalog.forms import NewsForm
from catalog import constants as Constants
from core import core_tools
import logging

logger = logging.getLogger(__name__)


CACHE = {}


def get_product_attributes(product_id):
    common_attrs = None
    selective_attrs = []
    p = Product.objects.get(id=product_id)
    variants = p.variants.all()
    attrs_qs = ProductAttribute.objects.none()
    attrs_dict_list = []
    attrs_qs_list = []
    for v in variants:
        attrs_dict_list.append({'variant_id':v.id, 'variant_uuid': v.product_uuid, 'attrs' : v.attributes.order_by('value')})
        attrs_qs_list.append(v.attributes.all())
    
    common_attrs = ProductAttribute.objects.intersection(*attrs_qs_list)
    for attr in attrs_dict_list:
        selective_attrs.append({'variant_id' : attr['variant_id'], 'variant_uuid': attr['variant_uuid'], 'attrs': attr['attrs'].difference(common_attrs)})

    return common_attrs, selective_attrs


def contain_attr(value, value_list):
    for e in value_list:
        if 'value' in e and e['value'] == value:
            return True
    return False

def clean_grouped_attrs(attrs):
    if not isinstance(attrs, dict):
        logger.warn("clean_grouped_attrs : attrs not of the type dict")
        return {}
    cleaned_attrs = attrs
    has_selective = False
    variant = None
    for k,v in cleaned_attrs.items():
        selective = len(v['value']) > 1
        has_selective = selective
        v['selective'] = selective
        if not selective:
            value = v['value'][0]
            variant = value['variant']
            v['value'].clear()
            v['value'] = value
    p_attrs = {
        'attrs' : cleaned_attrs,
        'has_selective' : has_selective
    }
    if not has_selective:
        p_attrs['variant'] = variant
    
    return p_attrs

def group_attrs(attrs):
    '''
    This method regroups products into an iterable
    attrs is a list of ProductAttribute represented as dict.
    example : 
    a product has the following variants attributes:
    {id, name, display_name, value, variant}
    id = attribute id, name = attribute name ... variant = the variant uuid that has this attribute for a defined product
    with a list of attributes as follow :
        {id=1, name="size", display_name="Size", value=30, variant=uuid_value_1}
        {id=2, name="size", display_name="Size", value=31, variant=uuid_value_2}
        {id=3, name="size", display_name="Size", value=32, variant=uuid_value_3}
        ...
        {id=4, name="color", display_name="Color", value="red", variant=uuid_value_4}
    
    calling group_attrs with these attributes will produce the following result :
        {size = {display_name=Size, value=[{variant=uuid_value_1, value=30},{variant=uuid_value_2, value=31},{variant=uuid_value_3, value=32}], selective=true}}
        {color = {display_name=Color, value="red", selective=false}
    '''
    if not isinstance(attrs, list):
        logger.warn("group_attrs : attrs not of the type list")
        return {}
    grouped_attrs = {}
    for attr in attrs:
        name = attr['name']
        if name not in grouped_attrs:
            grouped_attrs[name] = {'display_name' : attr['display_name'], 'variant': attr['variant'], 'value': [{'variant': attr['variant'], 'value': attr['value'], 'quantity': attr['quantity']}]}
        else:
            value = {'variant': attr['variant'], 'value': attr['value'], 'quantity': attr['quantity']}
            entry = grouped_attrs[name]
            if not contain_attr(value['value'], entry['value']):
                entry['value'].append(value)
    return clean_grouped_attrs(grouped_attrs)




## TODO  product_attributes need to be cached
def product_attributes(product_id):
    if not isinstance(product_id, int):
        logger.warn("product_attributes : product_id not of the type int")
        return {}
    key = Constants.CACHE_PRODUCT_ATTRIBUTES_PREFIX + str(product_id)
    if key in CACHE:
        return CACHE.get(key)
    variants = ProductVariant.objects.filter(product=product_id)
    attr_dict = {}
    attrs = []
    for v in variants:
        for attr in v.attributes.values('id', 'name', 'display_name', 'value'):
            attr['variant'] = v.product_uuid
            attr['quantity'] = v.quantity
            attrs.append(attr)
    if len(attrs):
        logger.info("Attrs available")
    else: 
        logger.info("Attrs not available")
    CACHE[key] = group_attrs(attrs)
    return CACHE[key]
    



def get_product_variant_attrs(product_id):
    """
    This method returns a tuple that contains two queryset :
    N.B : This method 

    1- queryset that represents the common attributes of variant product.
    Common attributes are those attribute have the same name - value pair  accross all variants.
    For example : color = black, material = lether

    2- queryset that represents the selectable attributes of variant product.
    Selectable attributes are attributes that have the same name but differents
    values accross all variants.
    For example : size = 32, size = 35, size= 38.
    This mean that the user can select a variant with a size attribute is one of 
    the 3 sizes listed above.

    
    """
    p = Product.objects.get(id=product_id)
    variants = p.variants.all()
    selectable_attr = ProductAttribute.objects.none()
    non_selectable_attr = ProductAttribute.objects.none()
    attr_queryset = ProductAttribute.objects.filter(products__in=variants)
    variants_count = variants.count()
    if variants_count == 1: 
        non_selectable_attr = attr_queryset
    elif variants_count > 1:   
        attr_values = attr_queryset.values('id', 'name', 'display_name', 'value').order_by('name').annotate(count=Count('name'))
        attribute = attr_values.filter(count=1).first()
        selectable_attr = {
            'name' : attribute.get('name'),
            'display_name' : attribute.get('display_name'),
            'attr_list': attr_values.filter(count=1)
        }
        non_selectable_attr = attr_values.filter(count__gt=1)
    return non_selectable_attr, selectable_attr

def get_variant_from_attr(attr_id, product):
    if product is None:
        return None
    p_variants = product.variants.all()
    attr = ProductAttribute.objects.filter(id=attr_id).first()
    variant = attr.products.filter(id__in=p_variants).first()
    logger.debug(f"get variant \"{variant}\" for attr \"{attr}\"")
    return variant


def update_default_attributes_primary():
    return ProductAttribute.objects.filter(name__in=Constants.DEFAULT_PRIMARY_ATTRIBUTES, is_primary=False).update(is_primary=True)

def toggle_attributes_primary(name_list=[], primary=True):
    if not isinstance(name_list, list) or not isinstance(primary, bool):
        return 0
    return ProductAttribute.objects.filter(Q(name__in=name_list)|Q(display_name__in=name_list), is_primary=False).update(is_primary=primary)



def create_news(data):
    news = core_tools.create_instance(model=News, data=data)
    if news:
        logger.info("News created")
    
    return news


def update_news(news, data):
    updated_news = core_tools.update_instance(model=News, instance=news, data=data)
    if updated_news:
        logger.info("News updated")
    
    return updated_news





def build_category_paths(category):
    if not isinstance(category, Category):
        return []
    key = Constants.CACHE_CATEGORY_PATH_PREFIX + category.name
    if key in CACHE:
        return CACHE.get(key)
    paths = [category]
    parent = category.parent
    while parent:
        paths.append(parent)
        parent = parent.parent
    paths.reverse()
    CACHE[key] = paths
    logger.info(f"Built paths from category {category.name} to roots : {paths}")
    return paths
    

def get_non_empty_root_category():
    roots = Category.objects.filter(parent=None, is_active=True)
    categories_with_products = Category.objects.exclude(parent=None).annotate(product_count=Count('products')).filter(product_count__gt=0)
    roots_cats = []
    logger.info(f"Categories withs products :")
    for c in categories_with_products:
        logger.info(f"Category : {c.name} - {c.display_name} - products : {c.product_count}" )
    return roots_cats


def category_descendants(category):
    if not isinstance(category, Category):
        return []
    key = Constants.CACHE_CATEGORY_DESCENDANTS_PREFIX + category.name
    if key in CACHE:
        return CACHE.get(key)
    queryset = Category.objects.raw(Constants.CATEGORY_DESCENDANTS_QUERY, [category.id])
    category_list = [c for c in queryset]
    category_list
    CACHE[key] = category_list
    return category_list


def category_products(category):
    if not isinstance(category, Category):
        return []
    key = Constants.CACHE_CATEGORY_PRODUCTS_PREFIX + category.name
    if key in CACHE:
        return CACHE.get(key)
    queryset = Product.objects.raw(Constants.CATEGORY_PRODUCT_QUERY, [category.id])
    product_list = [p for p in queryset]
    CACHE[key] = product_list
    return product_list