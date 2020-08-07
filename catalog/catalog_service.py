from django.db.models import Count
from catalog.models import Product, ProductAttribute, ProductVariant, ProductType, ProductTypeAttribute
import logging

logger = logging.getLogger(__name__)

def get_product_attributes(product_id):
    common_attrs = None
    selective_attrs = []
    p = Product.objects.get(id=product_id)
    variants = p.variants.all()
    attrs_qs = ProductAttribute.objects.none()
    attrs_dict_list = []
    attrs_qs_list = []
    for v in variants:
        attrs_dict_list.append({'variant_id':v.id, 'variant_uuid': v.product_uuid, 'attrs' : v.attributes.all()})
        attrs_qs_list.append(v.attributes.all())
    
    common_attrs = ProductAttribute.objects.intersection(*attrs_qs_list)
    for attr in attrs_dict_list:
        selective_attrs.append({'variant_id' : attr['variant_id'], 'variant_uuid': attr['variant_uuid'], 'attrs': attr['attrs'].difference(common_attrs)})

    return common_attrs, selective_attrs

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