from catalog.models import ProductAttribute
from catalog import models
from catalog import forms
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
    commons_attrs = {}
    common_names = []
    p_attrs = []
    for attr in queryset:
        name = attr['name']
        if name not in commons_attrs :
            commons_attrs[name] = [attr['id']]
        else:
            p_attrs.extend([attr['id'], commons_attrs[name][0]])
            del commons_attrs[name]
    logger.info(f"group_attributes : attrs = {attrs}")
    logger.info(f"Common Attrs : {commons_attrs}")
    logger.info(f"P_Attrs : {p_attrs}")
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




def update_product(postdata, product):
    if not isinstance(postdata, dict) or not isinstance(product, models.Product):
        return product, False
    updated = False
    p = product
    form = forms.ProductForm(postdata, instance=p)
    if form.is_valid():
        p = form.save()
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
    variant = None
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

        #variant = models.ProductVariant.objects.create(name=product.name, display_name=product.display_name,
        #        price=product.price, product=product)
        #variant.attributes.add(*attributes)
        logger.info(f'New Product Variant created ')
    else:
        logger.warn("Variant could not be created. No valid attributes submitted.")
    return variant
    
        




def create_instance(model, data):
    if not isinstance(model, Model) or not isinstance(data, dict):
        return None

    return model.objects.create(**data)


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

