from django.contrib.sitemaps import Sitemap
from catalog.models import Product, Brand, Category


class CategorySiteMap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return Category.objects.filter(is_active=True)
    
    def lastmod(self, obj):
        return obj.created_at