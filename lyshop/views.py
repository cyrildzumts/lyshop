from django.shortcuts import render, HttpResponseRedirect
from django.contrib import auth
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.contrib.sitemaps import Sitemap
from catalog.models import Highlight, Category
from catalog import constants as Catalog_Constants
# from django import forms
from django.contrib.auth.forms import UserCreationForm
from lyshop import settings

    

def page_not_found(request):
    template_name = '404.html'
    return render(request, template_name)


def server_error(request):
    template_name = '500.html'
    return render(request, template_name)

def permission_denied(request):
    template_name = '500.html'
    return render(request, template_name)

def bad_request(request):
    template_name = '500.html'
    return render(request, template_name)


def home(request):
    """
    This function serves the About Page.
    By default the About html page is saved
    on the root template folder.
    """
    template_name = "home.html"
    page_title = settings.SITE_NAME
    highlights = Highlight.objects.filter(is_active=True)
    parfum_category = Category.objects.get(name='parfum')
    context = {
        'page_title': page_title,
        'user_is_authenticated' : request.user.is_authenticated,
        'highlights' : highlights,
        'parfum_category' : parfum_category
    }
    return render(request, template_name,context)


def about(request):
    """
    This function serves the About Page.
    By default the About html page is saved
    on the root template folder.
    """
    template_name = "about.html"
    page_title = 'About' + ' - ' + settings.SITE_NAME
    context = {
        'page_title': page_title,
    }
    return render(request, template_name,context)



def faq(request):
    template_name = "faq.html"
    page_title = "FAQ" + ' - ' + settings.SITE_NAME
    context = {
        'page_title': page_title,
    }
    return render(request, template_name,context)


def customer_usage(request):
    template_name = "customer_usage.html"
    page_title =  "Customer Usage" + ' - ' + settings.SITE_NAME
    context = {
        'page_title': page_title
    }
    return render(request, template_name,context)





class LyshopSiteMap(Sitemap):
    changefreq = "montly"

    def items(self):
        return ["about", "faq", "home", "catalog:catalog-home"]
    
    def location(self, item):
        return reverse(item)