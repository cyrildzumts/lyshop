from django import forms
from django.contrib.auth.models import User
from catalog.models import Category, Product, ProductAttribute, ProductVariant, Brand, Policy, PolicyGroup, ProductImage, ProductType, ProductTypeAttribute

class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = ['name', 'display_name','code','added_by', 'is_active', 'parent']


class BrandForm(forms.ModelForm):

    class Meta:
        model = Brand
        fields = ['name', 'display_name', 'code', 'is_active']


class ProductAttributeForm(forms.ModelForm):

    class Meta:
        model = ProductAttribute
        fields = ['name', 'display_name', 'value', 'value_type']
    

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        value = cleaned_data.get('value')
        already_exist = ProductAttribute.objects.filter(name=name, value=value).exists()
        if already_exist:
            raise forms.ValidationError(f"Unique contraint on field name - \"{name}\" - and field value \"{value}\" violated")

        

class AttributeForm(forms.Form):

    attribute_name = forms.CharField(max_length=32)
    attribute_display_name = forms.CharField(max_length=32)
    attribute_value = forms.CharField(max_length=32)
    attribute_value_type = forms.IntegerField()




class ProductTypeAttributeForm(forms.ModelForm):

    class Meta:
        model = ProductTypeAttribute
        fields = ['name', 'display_name', 'description', 'attribute_type']



class ProductTypeForm(forms.ModelForm):

    class Meta:
        model = ProductType
        fields = ['name', 'display_name','is_active', 'code', 'attributes', 'type_attributes']


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = ['name', 'display_name','added_by', 'sold_by' ,'category', 'brand', 'product_type' ,'price', 'quantity', 'short_description','description', 'gender']


class AddAttributeForm(forms.ModelForm):

    class Meta:
        model = ProductVariant
        fields = ['attributes']


class DeleteAttributeForm(forms.ModelForm):

    class Meta:
        model = ProductVariant
        fields = ['attributes']


class ProductVariantForm(forms.ModelForm):

    class Meta:
        model = ProductVariant
        fields = ['name', 'display_name', 'product', 'attributes', 'price', 'quantity']


class ProductVariantUpdateForm(forms.ModelForm):

    class Meta:
        model = ProductVariant
        fields = ['name', 'display_name', 'product', 'attributes', 'price', 'quantity']



class ProductImageForm(forms.ModelForm):

    class Meta:
        model = ProductImage
        fields = ['name', 'product', 'image', 'product_variant']

class CategoriesDeleteForm(forms.Form):
    categories = forms.TypedMultipleChoiceField(coerce=int)