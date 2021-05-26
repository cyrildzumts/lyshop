from django.contrib.sitemaps import Sitemap
from django.templatetags.static import static
from django.shortcuts import reverse



class LyshopSiteMap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return ["home", "catalog:catalog-home", "about", "faq"]
    
    def location(self, item):
        return item.get_slug_url()