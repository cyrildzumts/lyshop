from django.urls import resolve
from django.urls import reverse
from django.test import TestCase
import unittest
#from django.contrib.auth import views as auth_views
from catalog import views
import uuid

# Create your tests here.
TEST_UUID = uuid.uuid4()

class CatalogViewsUrlTest(TestCase):
    def test_home_url(self):
        found = resolve('/catalog/')
        self.assertEqual(found.func, views.catalog_home)
        found = resolve(reverse('catalog:catalog-home'))
        self.assertEqual(found.func, views.catalog_home)

    def test_brand_detail_url(self):
        found = resolve(f'/catalog/brands/detail/{TEST_UUID}/')
        self.assertEqual(found.func, views.brand_detail)
        found = resolve(reverse('catalog:brand-detail', kwargs={'brand_uuid':TEST_UUID} ))
        self.assertEqual(found.func, views.brand_detail)


    def test_category_detail_url(self):
        found = resolve(f'/catalog/categories/detail/{TEST_UUID}/')
        self.assertEqual(found.func, views.category_detail)

        found = resolve(reverse('catalog:category-detail', kwargs={'category_uuid': TEST_UUID}))
        self.assertEqual(found.func, views.category_detail)


    def test_products_detail_url(self):
        found = resolve(f'/catalog/categories/products/detail/{TEST_UUID}/')
        self.assertEqual(found.func, views.product_detail)
        found = resolve(reverse('catalog:product-detail', kwargs={'product_uuid': TEST_UUID}))
        self.assertEqual(found.func, views.product_detail)

    def test_product_variant_detail_url(self):
        found = resolve(f'/catalog/categories/products/variant/detail/{TEST_UUID}/')
        self.assertEqual(found.func, views.product_variant_detail)

        found = resolve(reverse('catalog:product-variant-detail', kwargs={'variant_uuid': TEST_UUID}))
        self.assertEqual(found.func, views.product_variant_detail)


    def test_products_url(self):
        #found = resolve('/catalog/products/')
        ##self.assertEqual(found.func, views.ProductListView.as_view())
        pass

    
    def test_products_image_detail_url(self):
        found = resolve(f'/catalog/products/product-image/detail/{TEST_UUID}/')
        self.assertEqual(found.func, views.product_image_detail)

        found = resolve(reverse('catalog:product-image-detail', kwargs={'image_uuid': TEST_UUID}))
        self.assertEqual(found.func, views.product_image_detail)


