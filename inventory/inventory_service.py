from catalog.models import ProductAttribute
from catalog import models
from catalog import forms
from core import core_tools
from django.forms import formset_factory, modelformset_factory
from django.db.models import Model
from catalog import constants as Constants
import logging

logger = logging.getLogger(__name__)


def get_product_type_attributes(product):
    if not isinstance(product, models.Product):
        return []
    attributes = ProductAttribute.objects.none()
    type_attributes = models.ProductTypeAttribute.objects.filter(product_types__in=[product.product_type])
    names = []
    if type_attributes.exists():
        names = type_attributes.values_list('name')
        attributes = ProductAttribute.objects.filter(name__in=names)

    return attributes


def group_attributes(attrs):
    if not isinstance(attrs, list):
        return None
    queryset = models.ProductAttribute.objects.filter(pk__in=attrs).values('id', 'name')
    attributes = {}
    commons_attrs = []
    p_attrs = []
    for attr in queryset:
        name = attr['name']
        if name not in attributes :
            attributes[name] = [attr['id']]
        else:
            attributes[name].append(attr['id'])
    
    for name in attributes:
        if len(attributes[name]) > 1 :
            p_attrs.extend(attributes[name])
        elif len(attributes[name]) == 1 :
            commons_attrs.extend(attributes[name])

    return commons_attrs, p_attrs


def create_product(postdata):
    if not isinstance(postdata, dict):
        return None, False
    form = forms.ProductForm(postdata)
    p = None
    created = False
    if form.is_valid():
        p = form.save()
        logger.info(f"create_product : New Product {p.name} Created")
        created = True
    else:
        logger.error(f"Error when creating a new product : {form.errors}")
    return p, created


def create_product_from_data(data):
    if not isinstance(data, dict):
        return None, False
    p = None
    created = False
    try:
        p = models.Product.objects.create(**data)
        logger.info(f"create_product_from_data : New Product {p.name} Created")
        created = True
    except Exception as e :
        logger.warn(f"create_product_from_data : could not create New Product. Data = {data}", e)
    return p, created


def products_toggle_active(id_list, toggle=True):
    if not isinstance(id_list, list):
        return [], False
    if toggle:
        msg = f"Products \"{id_list}\" activated"
    else:
        msg = f"Products \"{id_list}\" deactivated"

    updated_row = core_tools.instances_active_toggle(models.Product, id_list, toggle)
    if updated_row > 0:
        #models.Product.objects.filter(id__in=id_list).exclude(is_active=toggle).update(is_active=toggle)
        logger.info(msg)
        return id_list, True
        
    else:
        logger.error(f"Products \"{id_list}\" could not update active status")
    return id_list, False


def products_toggle_sale(id_list, toggle=True):
    if not isinstance(id_list, list):
        return [], False
    if toggle:
        msg = f"Products \"{id_list}\" marked for sale"
    else:
        msg = f"Products \"{id_list}\" removed from sale"

    updated_row = core_tools.instances_sale_toggle(models.Product, id_list, toggle)
    if updated_row > 0:
        logger.info(msg)
        return id_list, True
        
    else:
        logger.error(f"Products \"{id_list}\" could not update active status")
    return id_list, False


def update_product(postdata, product):
    if not isinstance(postdata, dict) or not isinstance(product, models.Product):
        return product, False
    updated = False
    p = product
    form = forms.ProductForm(postdata, instance=p)
    if form.is_valid():
        sale = form.cleaned_data.get('promotion_price')
        
        sale = sale is not None and sale > 0
        form.cleaned_data['sale'] = sale
        logger.debug(f"update_product - sale : {sale}")
        p = form.save(commit=False)
        p.sale = sale
        p.save()
        form.save_m2m()
        logger.info(f"update_product : Product {p.name} updated")
        updated = True
    else:
        logger.warn(f"update_product : could not update Product {p.name}. Data = {postdata}")
    return p, updated



def update_product_from_data(data, product):
    if not isinstance(data, dict) or not isinstance(product, models.Product):
        return product, False
    p = product
    updated = False
    try:
        updated = models.Product.objects.filter(pk=product.pk).update(**data) == 1
        logger.info(f"update_product_from_data : Product {p.name} updated")
        created = True
    except Exception as e :
        logger.warn(f"update_product_from_data : could not update Product. Data = {data}", e)
    return p, created


# Check if there is no variant for that product with the same attributes
def create_variant(product, postdata):
    variants = []
    if not isinstance(postdata, dict) or not isinstance(product, models.Product):
        return variant
    
    created = False
    exists = models.ProductVariant.objects.filter()
    attribute_formset = modelformset_factory(models.ProductAttribute, form=forms.ProductAttributeForm)

    formset = attribute_formset(postdata)
    logger.info("Attribute formset valid checking")
    attributes = []
    key = 'attributes'
    new_attributes = ProductAttribute.objects.none()
    if key in postdata:
        attrs = postdata.getlist(key)
        attributes.extend(list(map(int, attrs)))


    if formset.is_valid():
        logger.info("create_variant : Attribute formset valid")
        new_attributes = formset.save()
        attributes.extend([attr.pk for attr in new_attributes])
    
    else:
        logger.error(f'Error on creating new product variant')
        logger.error(formset.errors)
    
    if attributes:
        commons_attrs, p_attrs = group_attributes(attributes)
        logger.debug(f"Variant create : common_attrs = {commons_attrs}, p_attrs = {p_attrs}")
        if len(p_attrs):
            for pk in p_attrs:
                logger.info(f'pk : {pk}')
                variant = models.ProductVariant.objects.create(name=product.name, display_name=product.display_name,
                        price=product.price, product=product)
                variant.attributes.add(*[pk, *commons_attrs])
                variants.append(variant)
            if len(variants):
                logger.info(f'New Product Variants({len(p_attrs)})  created ')
            else:
                logger.info(f'New Product Variants({len(p_attrs)})  not created ')
        else:
            variant = models.ProductVariant.objects.create(name=product.name, display_name=product.display_name,
                        price=product.price, product=product)
            variant.attributes.add(*commons_attrs)
            variants.append(variant)
            logger.info(f'New Product Variant created ')

    else:
        logger.warn("Variant could not be created. No valid attributes submitted.")
    return variants
    
        


def delete_instances(model, instances):
    if not isinstance(model, Model) or not isinstance(instances, list):
        return None, None
    return core_tools.delete_instances(model, instances)


def create_instance(model, data):
    if not isinstance(model, Model) or not isinstance(data, dict):
        return None

    return core_tools.create_instance(model, data)


def create_category(postdata):
    if not isinstance(postdata, dict):
        return None
    form = forms.CategoryForm(postdata)
    if form.is_valid():
        category = form.save()
        logger.info(f'[ OK ]New Category \"{category.name}\"' )
        return category
    else:
        logger.error(f'[ NOT OK ] Error on adding New Category. Errors : {form.errors}')
    return None


def update_category(postdata, category):
    if not isinstance(postdata, dict) or not isinstance(category, models.Category):
        return None, False
    form = forms.CategoryForm(postdata, instance=category)
    if form.is_valid():
        category = form.save()
        logger.info(f'[ OK ]New Category \"{category.name}\"' )
        return category, True
    else:
        logger.error(f'[ NOT OK ] Error on adding New Category. Errors : {form.errors}')
    return category, False


def create_brand(postdata):
    if not isinstance(postdata, dict):
        return None
    form = forms.BrandForm(postdata)
    if form.is_valid():
        brand = form.save()
        logger.info(f'[ OK ]New Brand \"{brand.name}\"' )
        return brand
    else:
        logger.error(f'[ NOT OK ] Error on adding New Brand. Errors : {form.errors}')
    return None


def update_brand(postdata, brand):
    if not isinstance(postdata, dict) or not isinstance(brand, models.Brand):
        return None, False
    form = forms.BrandForm(postdata, instance=brand)
    if form.is_valid():
        brand = form.save()
        logger.info(f'[ OK ]New Brand \"{brand.name}\"' )
        return brand, True
    else:
        logger.error(f'[ NOT OK ] Error on adding New Brand. Errors : {form.errors}')
    return brand, False


def create_attributes(postdata):
    if not isinstance(postdata, dict):
        return None, False
    attribute_formset = modelformset_factory(models.ProductAttribute, form=forms.ProductAttributeForm)
    formset = attribute_formset(postdata)
    if formset.is_valid():
        logger.info("Attributes formset valid")
        instances = formset.save()
        logger.info(f'New attributes created')
        return instances, True
    else:
        logger.error(f'Error on creating new attribute.')
        logger.error(formset.errors)
    return None, False

def bulk_create_attributes(postdata):
    if not isinstance(postdata, dict):
        return None, False
    form = forms.MassProductAttributeForm(postdata)
    if form.is_valid():
        name = form.cleaned_data.get('name')
        display_name = form.cleaned_data.get('display_name')
        value_type = form.cleaned_data.get('value_type')
        is_primary = form.cleaned_data.get('is_primary')
        range_start = form.cleaned_data.get('range_start')
        range_end = form.cleaned_data.get('range_end')
        attrs = [models.ProductAttribute.objects.create(name=name, display_name=display_name, value_type=value_type, is_primary=is_primary, value=value) for value in range(range_start, range_end + 1)]
        return attrs, True
    else:
        logger.error(f"error on create mass ProductAttribute. Error : {form.errors}")
    return None, False


def delete_attributes(attrs):
    if not isinstance(attrs, list):
        return False
    return models.ProductAttribute.objects.filter(id__in=attrs).delete()



def update_attribute(postdata, attribute):
    if not isinstance(postdata, dict) or not isinstance(attribute, models.ProductAttribute):
        return None, False
    form = forms.ProductAttributeForm(postdata, instance=attribute)
    if form.is_valid():
        attribute = form.save()
        logger.info(f'Attribute updated')
        return attribute, True
    else:
        logger.error(f'Error on updated Attribute.')
    return attribute, False
    


def create_product_type(postdata):
    if not isinstance(postdata, dict):
        return None
    form = forms.ProductTypeForm(postdata)
    if form.is_valid():
        product_type = form.save()
        logger.info(f'[ OK ]New ProductType \"{product_type.name}\"' )
        return product_type
    else:
        logger.error(f'[ NOT OK ] Error on adding New ProductType. Errors : {form.errors}')
    return None


def update_product_type(postdata, product_type):
    if not isinstance(postdata, dict) or not isinstance(product_type, models.ProductType):
        return None, False
    form = forms.ProductTypeForm(postdata, instance=product_type)
    if form.is_valid():
        product_type = form.save()
        logger.info(f'ProductType updated')
        return product_type, True
    else:
        logger.error(f'Error when updating ProductType.')
    return product_type, False


def get_top_10():
    return models.Product.objects.filter(is_active=True).order_by('-view_count')[:Constants.TOP_VIEWS_MAX]



def get_recommandations(product):
    if not isinstance(product, models.Product):
        return models.Product.objects.none()
    return models.Product.objects.filter(is_active=True, category=product.category, gender=product.gender).exclude(pk=product.pk).order_by('-view_count')[:Constants.TOP_VIEWS_MAX]