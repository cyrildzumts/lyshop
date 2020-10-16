from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.urls import reverse
from catalog import constants
from lyshop import conf
import uuid
import logging

logger = logging.getLogger(__name__)

# Create your models here.


class Policy(models.Model):
    """
        Every Business account has a policy set. This policy defines the 
        transfer limit applied to the business account.
        For every transfer going to a business account a commission fee is extracted from 
        the transfer amount. This fee is added the PAY account.
        The daily_limit is maximal amount allowed to be received by a business account in a day.
        The weekly_limit is maximal amount allowed to be received by a business account in a week.
        The monthly_limit is maximal amount allowed to be received by a business account in a month.
        The commission is a percent value that is to be taken from the transfer amount.

    """
    daily_limit = models.IntegerField(blank=False)
    weekly_limit = models.IntegerField(blank=False)
    monthly_limit = models.IntegerField(blank=False)
    commission = models.DecimalField(max_digits=conf.COMMISSION_MAX_DIGITS, decimal_places=conf.COMMISSION_DECIMAL_PLACES, default=conf.COMMISSION_DEFAULT)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User, related_name="modified_policies", unique=False, null=True,blank=True, on_delete=models.SET_NULL)
    policy_uuid = models.UUIDField(default=uuid.uuid4, editable=False)



    def __str__(self):
        return "Policy {0}".format(self.commission)

    def get_absolute_url(self):
        return reverse("payment:policy-detail", kwargs={"policy_uuid": self.policy_uuid})
    
    def get_dashboard_url(self):
        return reverse("dashboard:policy-detail", kwargs={"policy_uuid": self.policy_uuid})
    
    def get_delete_url(self):
        return reverse("dashboard:policy-remove", kwargs={"policy_uuid": self.policy_uuid})
    
    def get_update_url(self):
        return reverse("dashboard:policy-update", kwargs={"policy_uuid": self.policy_uuid})


class PolicyGroup(models.Model):
    name = models.CharField(max_length=80)
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name='policy_group')
    members = models.ManyToManyField(User, through='PolicyMembership', through_fields=('group', 'user'), blank=True)
    policy_group_uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("payments:policy-group", kwargs={"group_uuid": self.policy_group_uuid})
    
    def get_dashboard_url(self):
        return reverse("dashboard:policy-group-detail", kwargs={"group_uuid": self.policy_group_uuid})

    def get_update_url(self):
        return reverse("dashboard:policy-group-update", kwargs={"group_uuid": self.policy_group_uuid})
    
    def get_delete_url(self):
        return reverse("dashboard:policy-group-remove", kwargs={"group_uuid": self.policy_group_uuid})



class PolicyMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(PolicyGroup, on_delete=models.CASCADE)
    policy_membership_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User, related_name="modified_membership", unique=False, null=True,blank=True, on_delete=models.SET_NULL)
    added_by = models.ForeignKey(User, related_name="added_membership", unique=False, null=True,blank=True, on_delete=models.SET_NULL)



class Category(models.Model):
    name = models.CharField(max_length=32, null=False, blank=False)
    display_name = models.CharField(max_length=32, null=True, blank=True)
    code = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addeds_categories', blank=False, null=False)
    is_active = models.BooleanField(default=True, blank=True)
    view_count = models.IntegerField(blank=True, null=True, default=0)
    parent = models.ForeignKey('self', related_name='children', blank=True, null=True, on_delete=models.SET_NULL)
    category_uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.name
    
    def get_children(self):
        return Category.objects.filter(parent=self)
    
    def get_absolute_url(self):
        return reverse("catalog:category-detail", kwargs={"category_uuid": self.category_uuid})
    
    def get_dashboard_url(self):
        return reverse("dashboard:category-detail", kwargs={"category_uuid": self.category_uuid})
    
    def get_update_url(self):
        return reverse("dashboard:category-update", kwargs={"category_uuid": self.category_uuid})
    
    def get_delete_url(self):
        return reverse("dashboard:category-delete", kwargs={"category_uuid": self.category_uuid})


class Brand(models.Model):
    name = models.CharField(max_length=32, null=False, blank=False)
    display_name = models.CharField(max_length=32, null=True, blank=True)
    code = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='addeds_brands', blank=False, null=True)
    is_active = models.BooleanField(default=True)
    view_count = models.IntegerField(blank=True, null=True, default=0)
    brand_uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("catalog:brand-detail", kwargs={"brand_uuid": self.brand_uuid})
    
    def get_dashboard_url(self):
        return reverse("dashboard:brand-detail", kwargs={"brand_uuid": self.brand_uuid})

    def get_update_url(self):
        return reverse("dashboard:brand-update", kwargs={"brand_uuid": self.brand_uuid})

    def get_vendor_url(self):
        return reverse("vendors:brand-detail", kwargs={"brand_uuid": self.brand_uuid})

    def get_vendor_update_url(self):
        return reverse("vendors:brand-update", kwargs={"brand_uuid": self.brand_uuid})

    def get_vendor_delete_url(self):
        return reverse("vendors:brand-delete", kwargs={"brand_uuid": self.brand_uuid})


class ProductAttribute(models.Model):

    name = models.CharField(max_length=32, null=False, blank=False)
    value = models.CharField(max_length=32, null=False, blank=False)
    value_type = models.IntegerField(default=constants.ATTRIBUTE_TYPE_DEFAULT ,null=False, blank=False, choices=constants.ATTRIBUTE_TYPE)
    display_name = models.CharField(max_length=32, null=False, blank=False)
    attribute_uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    class Meta:
        unique_together = ['name', 'value']
        ordering = ['name']

    def __str__(self):
        return f"{self.display_name} - {self.value}" 
    
    def get_dashboard_url(self):
        return reverse("dashboard:attribute-detail", kwargs={"attribute_uuid": self.attribute_uuid})

    def get_vendor_url(self):
        return reverse("vendors:attribute-detail", kwargs={"attribute_uuid": self.attribute_uuid})

    def get_update_url(self):
        return reverse("dashboard:attribute-update", kwargs={"attribute_uuid": self.attribute_uuid})
    
    def get_vendor_update_url(self):
        return reverse("vendors:attribute-update", kwargs={"attribute_uuid": self.attribute_uuid})

    def get_delete_url(self):
        return reverse("dashboard:attribute-delete", kwargs={"attribute_uuid": self.attribute_uuid})


class ProductTypeAttribute(models.Model):

    name = models.CharField(max_length=32, null=False, blank=False)
    display_name = models.CharField(max_length=32, null=True, blank=True)
    attribute_type = models.IntegerField(constants.ATTRIBUTE_TYPE_STRING)
    description = models.CharField(max_length=164)
    type_attribute_uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    def get_dashboard_url(self):
        return reverse("dashboard:product-type-attribute-detail", kwargs={"type_attribute_uuid": self.type_attribute_uuid})

    def get_update_url(self):
        return reverse("dashboard:product-type-attribute-update", kwargs={"type_attribute_uuid": self.type_attribute_uuid})

    def get_vendor_url(self):
        return reverse("vendors:product-type-attribute-detail", kwargs={"type_attribute_uuid": self.type_attribute_uuid})

    def get_vendor_update_url(self):
        return reverse("vendors:product-type-attribute-update", kwargs={"type_attribute_uuid": self.type_attribute_uuid})

    def get_delete_url(self):
        return reverse("dashboard:product-type-attribute-delete", kwargs={"type_attribute_uuid": self.type_attribute_uuid})



class ProductType(models.Model):
    name = models.CharField(max_length=50)
    display_name = models.CharField(max_length=32, null=False, blank=False)
    code = models.IntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    attributes = models.ManyToManyField(ProductAttribute, related_name='product_types', blank=True, null=True)
    type_attributes = models.ManyToManyField(ProductTypeAttribute, related_name='product_types', blank=True, null=True)
    type_uuid = models.UUIDField(default=uuid.uuid4, editable=False)


    def __str__(self):
        return self.name
    
    def get_dashboard_url(self):
        return reverse("dashboard:product-type-detail", kwargs={"type_uuid": self.type_uuid})

    def get_update_url(self):
        return reverse("dashboard:product-type-update", kwargs={"type_uuid": self.type_uuid})
    
    def get_absolute_url(self):
        return reverse("dashboard:product-type-detail", kwargs={"type_uuid": self.type_uuid})

    
    def get_vendor_url(self):
        return reverse("vendors:product-type-detail", kwargs={"type_uuid": self.type_uuid})

    def get_vendor_update_url(self):
        return reverse("vendors:product-type-update", kwargs={"type_uuid": self.type_uuid})
    

    



class Product(models.Model):
    name = models.CharField(max_length=32, null=False, blank=False)
    product_type = models.ForeignKey(ProductType, related_name="products", on_delete=models.SET_NULL, blank=True, null=True)
    display_name = models.CharField(max_length=32, null=True, blank=True)
    article_number = models.IntegerField(blank=True, null=True)
    category = models.ForeignKey(Category,related_name='products', on_delete=models.SET_NULL, blank=True, null=True)
    brand = models.ForeignKey(Brand,related_name='products', on_delete=models.SET_NULL, blank=True, null=True)
    is_active = models.BooleanField(default=False)
    price = models.DecimalField(blank=False, null=False, max_digits=conf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=conf.PRODUCT_PRICE_DECIMAL_PLACES)
    promotion_price = models.DecimalField(blank=True, null=True, max_digits=conf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=conf.PRODUCT_PRICE_DECIMAL_PLACES)
    quantity = models.IntegerField(default=1)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addeds_products', blank=False, null=False)
    sold_by = models.ForeignKey(User,on_delete=models.SET_NULL, related_name='sold_products', blank=True, null=True)
    viewed_by = models.ManyToManyField(User, related_name='viewed_products', blank=True)
    bought_by = models.ManyToManyField(User, related_name='bought_products', blank=True)
    short_description = models.CharField(max_length=164)
    description = models.TextField(blank=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    last_edited_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    gender = models.IntegerField(blank=True, null=True, choices=constants.GENDER)
    view_count = models.IntegerField(blank=True, null=True, default=0)
    product_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    FILTERABLE_FIELDS = ['brand', 'gender', 'price', 'product_type' ]
    FILTER_CONFIG = {
        'model' : 'Product',
        'fields' : FILTERABLE_FIELDS,
        'price' : {'field_name': 'price','template_name' : 'tags/decimal_field.html', 'range': True, 'selection' : False, 'selection_options' : ()},
        'brand' : {'field_name': 'brand','template_name' : 'tags/integer_field.html','range': False, 'selection' : True, 'queryset':True, 'selection_options' : Brand.objects.all()},
        'product_type' : {'field_name': 'product_type','template_name' : 'tags/integer_field.html','range': False, 'selection' : True, 'queryset':True, 'selection_options' : ProductType.objects.all()},
        'gender' : {'field_name': 'genre','template_name' : 'tags/integer_field.html', 'range': False, 'selection' : True, 'queryset':False, 'selection_options' : constants.GENDER},
    }

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("catalog:product-detail", kwargs={"product_uuid": self.product_uuid})
    
    
    def get_dashboard_url(self):
        return reverse("dashboard:product-detail", kwargs={"product_uuid": self.product_uuid})
    
    def get_update_url(self):
        return reverse("dashboard:product-update", kwargs={"product_uuid": self.product_uuid})
    
    def get_delete_url(self):
        return reverse("dashboard:product-delete", kwargs={"product_uuid": self.product_uuid})

    def get_vendor_url(self):
        return reverse("vendors:product-detail", kwargs={"product_uuid": self.product_uuid})
    
    def get_vendor_update_url(self):
        return reverse("vendors:product-update", kwargs={"product_uuid": self.product_uuid})
    
    def get_vendor_delete_url(self):
        return reverse("vendors:product-delete", kwargs={"product_uuid": self.product_uuid})

    
    @property
    def get_promotion_price(self):
        return self.promotion_price or 0

    @property
    def active_price(self):
        return self.promotion_price or self.price
    
    @property
    def is_promoted(self):
        return self.promotion_price is not None
    

class SKUModel(models.Model):
    sku = models.CharField(max_length=32,blank=False, null=False)

    def __str__(self):
        return f"SKU {self.sku}"
     


class ProductVariant(models.Model):
    name = models.CharField(max_length=32, null=False, blank=False)
    display_name = models.CharField(max_length=32, null=True, blank=True)
    sku = models.CharField(max_length=32,blank=True, null=True)
    article_number = models.CharField(max_length=32,blank=True, null=True)
    product = models.ForeignKey(Product, related_name='variants' ,on_delete=models.CASCADE, blank=False, null=False)
    is_active = models.BooleanField(default=False)
    attributes = models.ManyToManyField(ProductAttribute, related_name='products', null=True, blank=True)
    price = models.DecimalField(blank=False, null=False, max_digits=conf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=conf.PRODUCT_PRICE_DECIMAL_PLACES)
    promotion_price = models.DecimalField(blank=True, null=True, max_digits=conf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=conf.PRODUCT_PRICE_DECIMAL_PLACES)
    quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    last_edited_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    product_uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("catalog:product-variant-detail", kwargs={"variant_uuid": self.product_uuid})
    
    def get_dashboard_url(self):
        return reverse("dashboard:product-variant-detail", kwargs={"variant_uuid": self.product_uuid})
    
    def get_update_url(self):
        return reverse("dashboard:product-variant-update", kwargs={"variant_uuid": self.product_uuid})
    
    def get_delete_url(self):
        return reverse("dashboard:product-variant-delete", kwargs={"variant_uuid": self.product_uuid})

    def get_vendor_url(self):
        return reverse("vendors:product-variant-detail", kwargs={"variant_uuid": self.product_uuid})

    def get_vendor_update_url(self):
        return reverse("vendors:product-variant-update", kwargs={"variant_uuid": self.product_uuid})

    
    def get_vendor_delete_url(self):
        return reverse("vendors:product-variant-delete", kwargs={"variant_uuid": self.product_uuid})

    @property
    def get_promotion_price(self):
        return self.promotion_price or self.product.promotion_price

    @property
    def active_price(self):
        return self.promotion_price or self.product.promotion_price or self.price

    @property
    def is_promoted(self):
        return self.promotion_price is not None or self.product.is_promoted



def upload_to(instance, filename):
    #return f"products/{instance.product.id}/{instance.name}/{instance.product.id}-{instance.height}x{instance.width}-{filename}"
    return f"products/{instance.product.id}/{instance.product.category.code}-{instance.product.id}-{instance.height}x{instance.width}-{filename}"


class ProductImage(models.Model):
    height = models.IntegerField(blank=True, null=True)
    width = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=32, null=False, blank=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='images', blank=True, null=True)
    image = models.ImageField(upload_to=upload_to, height_field='height', width_field='width')
    is_main_image = models.BooleanField(default=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    last_edited_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    image_uuid = models.UUIDField(default=uuid.uuid4, editable=False)


    def delete_image_file(self):
        self.image.delete(False)

    def get_image_url(self):
        return self.image.url
    
    def get_absolute_url(self):
        return reverse("catalog:product-image-detail", kwargs={"image_uuid": self.image_uuid})
    
    def get_dashboard_url(self):
        return reverse("dashboard:product-image-detail", kwargs={"image_uuid": self.image_uuid})
    
    def get_update_url(self):
        return reverse("dashboard:product-image-update", kwargs={"image_uuid": self.image_uuid})

    def get_delete_url(self):
        return reverse("dashboard:product-image-delete", kwargs={"image_uuid": self.image_uuid})


    def get_vendor_url(self):
        return reverse("vendors:product-image-detail", kwargs={"image_uuid": self.image_uuid})
    
    def get_vendor_update_url(self):
        return reverse("vendors:product-image-update", kwargs={"image_uuid": self.image_uuid})

    def get_vendor_delete_url(self):
        return reverse("vendors:product-image-delete", kwargs={"image_uuid": self.image_uuid})




@receiver(post_save, sender=ProductVariant)
def generate_product_sku(sender, instance, created, **kwargs):
    if created:
        logger.debug(f'Generating SKU for newly created Product variant {instance.name}')
        sku = f"{instance.product.category.code}{instance.product.brand.code}" + str(instance.id).zfill(conf.PRODUCT_NUMBER_LENGTH)
        logger.debug(f'SKU for Product variant {instance.name} generated : {sku}')
        if ProductVariant.objects.filter(pk=instance.pk).exists():
            logger.debug("Saving generated SKU in the product ...")
            try :
                updated_rows_count = ProductVariant.objects.filter(pk=instance.pk).update(sku=sku, article_number=sku)
                logger.info(f"[ OK ] SKU created for Product Variant {instance.name}. affected Rows : {updated_rows_count}")
            except Exception as e:
                logger.error(f"[ ERROR ] SKU created but could not update Product Variant {instance.name}.")
                logger.exception(e)
        else :
            logger.debug("[ FAILED ] SKU not saved in new ProductVariant : instance not found in the database")
        