from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save, post_save
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
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
    name = models.CharField(max_length=64)
    display_name = models.CharField(max_length=64)
    page_title_index = models.IntegerField(null=True, choices=constants.CATEGORIES)
    code = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addeds_categories', blank=False, null=False)
    is_active = models.BooleanField(default=True)
    view_count = models.IntegerField(blank=True, null=True, default=0)
    parent = models.ForeignKey('self', related_name='children', blank=True, null=True, on_delete=models.SET_NULL)
    slug = models.SlugField(max_length=250, blank=True, null=True)
    description = models.CharField(max_length=constants.CATEGORY_DESCRIPTION_MAX_SIZE, blank=True, null=True)
    category_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    FORM_FIELDS = ['name', 'display_name','page_title_index', 'code', 'parent', 'added_by', 'is_active']

    def __str__(self):
        return f"{self.name} - {self.display_name}"
    
    def get_children(self):
        return Category.objects.filter(parent=self)
    
    def get_absolute_url(self):
        return reverse("catalog:category-detail", kwargs={"category_uuid": self.category_uuid})
    
    def get_slug_url(self):
        return reverse("catalog:category-detail", kwargs={"slug": self.slug})
    
    def get_dashboard_url(self):
        return reverse("dashboard:category-detail", kwargs={"category_uuid": self.category_uuid})
    
    def get_update_url(self):
        return reverse("dashboard:category-update", kwargs={"category_uuid": self.category_uuid})
    
    def get_delete_url(self):
        return reverse("dashboard:category-delete", kwargs={"category_uuid": self.category_uuid})
    
    def get_page_title(self):
        k, v = constants.get_category_page_title(self.page_title_index)
        return v or _(self.display_name)


class Brand(models.Model):
    name = models.CharField(max_length=64)
    display_name = models.CharField(max_length=64)
    code = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='addeds_brands', blank=False, null=True)
    is_active = models.BooleanField(default=True)
    view_count = models.IntegerField(blank=True, null=True, default=0)
    brand_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    FORM_FIELDS = ['name', 'display_name', 'code', 'added_by', 'is_active']

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

    name = models.CharField(max_length=64)
    value = models.CharField(max_length=64)
    value_type = models.IntegerField(default=constants.ATTRIBUTE_TYPE_DEFAULT ,null=False, blank=False, choices=constants.ATTRIBUTE_TYPE)
    is_primary = models.BooleanField(default=False)
    display_name = models.CharField(max_length=64)
    attribute_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    FORM_FIELDS = ['name', 'display_name', 'value', 'value_type', 'is_primary']

    class Meta:
        unique_together = ['name', 'value']
        ordering = ['name', 'value']

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

    name = models.CharField(max_length=64)
    display_name = models.CharField(max_length=64)
    attribute_type = models.IntegerField(constants.ATTRIBUTE_TYPE_STRING)
    attributes = models.ManyToManyField(ProductAttribute, related_name='type_attributes', blank=True, null=True)
    description = models.CharField(max_length=164)
    type_attribute_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    FORM_FIELDS = ['name', 'display_name', 'attribute_type', 'attributes', 'description']

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
    name = models.CharField(max_length=64)
    display_name = models.CharField(max_length=64, null=False, blank=False)
    code = models.IntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    attributes = models.ManyToManyField(ProductAttribute, related_name='product_types', blank=True, null=True)
    type_attributes = models.ManyToManyField(ProductTypeAttribute, related_name='product_types', blank=True, null=True)
    type_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    FORM_FIELDS = ['name', 'display_name', 'code', 'is_active', 'attributes', 'type_attributes']


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
    name = models.CharField(max_length=64)
    product_type = models.ForeignKey(ProductType, related_name="products", on_delete=models.SET_NULL, blank=True, null=True)
    display_name = models.CharField(max_length=64)
    article_number = models.IntegerField(blank=True, null=True)
    category = models.ForeignKey(Category,related_name='products', on_delete=models.SET_NULL, blank=True, null=True)
    brand = models.ForeignKey(Brand,related_name='products', on_delete=models.SET_NULL, blank=True, null=True)
    is_active = models.BooleanField(default=False)
    sale = models.BooleanField(default=False)
    price = models.DecimalField(blank=False, null=False, max_digits=conf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=conf.PRODUCT_PRICE_DECIMAL_PLACES)
    promotion_price = models.DecimalField(blank=True, null=True, max_digits=conf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=conf.PRODUCT_PRICE_DECIMAL_PLACES)
    quantity = models.IntegerField(default=0)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addeds_products', blank=False, null=False)
    sold_by = models.ForeignKey(User,on_delete=models.SET_NULL, related_name='sold_products', blank=True, null=True)
    viewed_by = models.ManyToManyField(User, related_name='viewed_products', blank=True)
    bought_by = models.ManyToManyField(User, related_name='bought_products', blank=True)
    short_description = models.CharField(max_length=constants.SHORT_DESCRIPTION_MAX_SIZE)
    description = models.TextField(blank=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    last_edited_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    gender = models.IntegerField(blank=True, null=True, choices=constants.GENDER)
    slug = models.SlugField(max_length=250, blank=True, null=True)
    view_count = models.IntegerField(blank=True, null=True, default=0)
    related_products = models.ManyToManyField('self')
    product_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    FORM_FIELDS = ['name', 'display_name', 'product_type', 'category','brand', 'is_active', 'price', 'promotion_price','quantity','sold_by','short_description'
    ,'description','gender', 'related_products', 'added_by']
    FILTERABLE_FIELDS = ['brand', 'created_at','gender', 'price', 'product_type', 'promotion_price', 'quantity' ]
    CATALOGUE_FILTERABLE_FIELDS = ['brand','gender', 'price', 'product_type' ]
    FILTER_CONFIG = {
        'model' : 'Product',
        'fields' : FILTERABLE_FIELDS,
        'created_at' : {'field_name': 'created_at','display_name': 'Created at', 'template_name' : 'tags/datetime_field.html', 'range': True, 'selection' : False, 'selection_options' : ()},
        'quantity' : {'field_name': 'quantity','display_name': 'Quantity', 'template_name' : 'tags/integer_field.html', 'range': True, 'selection' : False, 'selection_options' : ()},
        'price' : {'field_name': 'price','display_name': 'Price', 'template_name' : 'tags/decimal_field.html', 'range': True, 'selection' : False, 'selection_options' : ()},
        'promotion_price' : {'field_name': 'promotion_price','display_name': 'Promotion Price', 'template_name' : 'tags/decimal_field.html', 'range': True, 'selection' : False, 'selection_options' : ()},
        'brand' : {'field_name': 'brand','display_name': 'Brand', 'template_name' : 'tags/integer_field.html','range': False, 'selection' : True, 'queryset':True, 'selection_options' : Brand.objects.all()},
        'product_type' : {'field_name': 'product_type','display_name': 'Product Type', 'template_name' : 'tags/integer_field.html','range': False, 'selection' : True, 'queryset':True, 'selection_options' : ProductType.objects.all()},
        'gender' : {'field_name': 'genre','display_name': 'Gender', 'template_name' : 'tags/integer_field.html', 'range': False, 'selection' : True, 'queryset':False, 'selection_options' : constants.GENDER},
    }
    CATALOGUE_FILTER_CONFIG = {
        'model' : 'Product',
        'fields' : CATALOGUE_FILTERABLE_FIELDS,
        'price' : {'field_name': 'price','display_name': 'Price', 'template_name' : 'tags/decimal_field.html', 'range': True, 'selection' : False, 'selection_options' : ()},
        'brand' : {'field_name': 'brand','display_name': 'Brand', 'template_name' : 'tags/integer_field.html','range': False, 'selection' : True, 'queryset':True, 'selection_options' : Brand.objects.all()},
        'product_type' : {'field_name': 'product_type','display_name': 'Product Type', 'template_name' : 'tags/integer_field.html','range': False, 'selection' : True, 'queryset':True, 'selection_options' : ProductType.objects.all()},
        'gender' : {'field_name': 'genre','display_name': 'Gender', 'template_name' : 'tags/integer_field.html', 'range': False, 'selection' : True, 'queryset':False, 'selection_options' : constants.GENDER},
    }

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("catalog:product-detail", kwargs={"product_uuid": self.product_uuid})
    
    def get_slug_url(self):
        return reverse("catalog:product-detail", kwargs={"product_slug": self.slug, "category_slug": self.category.slug, "product_uuid" : self.product_uuid})
    
    
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
        return self.promotion_price is not None and self.promotion_price > 0
    
    @property
    def image(self):
        if self.images.exists():
            return self.images.first().get_image_url()
    

class SKUModel(models.Model):
    sku = models.CharField(max_length=32,blank=False, null=False)

    def __str__(self):
        return f"SKU {self.sku}"
     


class ProductVariant(models.Model):
    name = models.CharField(max_length=64)
    display_name = models.CharField(max_length=64, null=True, blank=True)
    sku = models.CharField(max_length=64,blank=True, null=True)
    article_number = models.CharField(max_length=64,blank=True, null=True)
    product = models.ForeignKey(Product, related_name='variants' ,on_delete=models.CASCADE, blank=False, null=False)
    is_active = models.BooleanField(default=False)
    attributes = models.ManyToManyField(ProductAttribute, related_name='products', null=True, blank=True)
    price = models.DecimalField(blank=False, null=False, max_digits=conf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=conf.PRODUCT_PRICE_DECIMAL_PLACES)
    promotion_price = models.DecimalField(blank=True, null=True, max_digits=conf.PRODUCT_PRICE_MAX_DIGITS, decimal_places=conf.PRODUCT_PRICE_DECIMAL_PLACES)
    quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    last_edited_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    product_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    FORM_FIELDS = ['name', 'display_name', 'product', 'is_active', 'price', 'promotion_price','quantity','attributes','short_description']

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

    @property
    def image(self):
        if self.images.exists():
            return self.images.first().get_image_url()
       
        return self.product.image



def upload_to(instance, filename):
    #return f"products/{instance.product.id}/{instance.name}/{instance.product.id}-{instance.height}x{instance.width}-{filename}"
    return f"products/{instance.product.id}/{instance.product.category.code}-{instance.product.id}-{instance.height}x{instance.width}-{filename}"


class ProductImage(models.Model):
    height = models.IntegerField(blank=True, null=True)
    width = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=64, null=False, blank=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='images', blank=True, null=True)
    image = models.ImageField(upload_to=upload_to, height_field='height', width_field='width')
    is_main_image = models.BooleanField(default=True)
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



class RelatedProduct(models.Model):
    name = models.CharField(max_length=64, null=False, blank=False)
    product = models.ForeignKey(Product, related_name='related_product', on_delete=models.CASCADE)
    related_products = models.ManyToManyField(Product)
    FORM_FIELDS = ['name', 'product', 'related_products']


class Highlight(models.Model):
    name = models.CharField(max_length=64, null=False, blank=False)
    display_name = models.CharField(max_length=64, null=False, blank=False)
    gender = models.IntegerField(default=constants.GENDER_WOMEN, choices=constants.GENDER, blank=True, null=True)
    products = models.ManyToManyField(Product, blank=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    last_edited_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    description = models.CharField(max_length=constants.DESCRIPTION_MAX_SIZE, blank=True, null=True)
    highlight_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    FORM_FIELDS = ['name','display_name', 'gender', 'is_active', 'products', 'description']

    def get_absolute_url(self):
        return reverse("dashboard:highlight-detail", kwargs={"highlight_uuid": self.highlight_uuid})
    
    
    def get_dashboard_url(self):
        return reverse("dashboard:highlight-detail", kwargs={"highlight_uuid": self.highlight_uuid})
    
    def get_update_url(self):
        return reverse("dashboard:highlight-update", kwargs={"highlight_uuid": self.highlight_uuid})
    
    def get_delete_url(self):
        return reverse("dashboard:highlight-delete", kwargs={"highlight_uuid": self.highlight_uuid})

    def get_vendor_url(self):
        return reverse("vendors:highlight-detail", kwargs={"highlight_uuid": self.highlight_uuid})
    
    def get_vendor_update_url(self):
        return reverse("vendors:highlight-update", kwargs={"highlight_uuid": self.highlight_uuid})
    
    def get_vendor_delete_url(self):
        return reverse("vendors:highlight-delete", kwargs={"highlight_uuid": self.highlight_uuid})


class News(models.Model):
    title = models.CharField(max_length=128)
    content = models.CharField(max_length=256)
    is_active = models.BooleanField(default=False)
    added_by = models.ForeignKey(User, related_name='added_news', blank=True, null=True, on_delete=models.SET_NULL)
    changed_by = models.ForeignKey(User, related_name='edited_news', blank=True, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False, editable=False)
    last_changed_at = models.DateTimeField(auto_now=True)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    news_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    FORM_FIELDS = ['title', 'content', 'is_active', 'added_by', 'changed_by', 'start_at', 'end_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("dashboard:news-detail", kwargs={"news_uuid": self.news_uuid})
    
    def get_delete_url(self):
        return reverse("dashboard:news-delete", kwargs={"news_uuid": self.news_uuid})

    def get_update_url(self):
        return reverse("dashboard:news-update", kwargs={"news_uuid": self.news_uuid})




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


