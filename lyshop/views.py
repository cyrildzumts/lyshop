from django.shortcuts import render, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import auth
from django.templatetags.static import static
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
    page_title = settings.HOME_TITLE
    highlights = Highlight.objects.filter(is_active=True)
    try:
        parfum_category = Category.objects.get(name='parfum')
    except ObjectDoesNotExist as identifier:
        parfum_category = None

    try:
        mode_category = Category.objects.get(name='mode')
    except ObjectDoesNotExist as identifier:
        mode_category = None
    
    try:
        electronics_category = Category.objects.get(name='electronic')
    except ObjectDoesNotExist as identifier:
        electronics_category = None
    
    context = {
        'page_title': page_title,
        'user_is_authenticated' : request.user.is_authenticated,
        'highlights' : highlights,
        'parfum_category' : parfum_category,
        'mode_category': mode_category,
        'electronics_category' : electronics_category,
        'OG_TITLE' : page_title,
        'OG_DESCRIPTION': settings.META_DESCRIPTION,
        'OG_IMAGE': static('assets/lyshop_banner.png'),
        'OG_URL': request.build_absolute_uri()
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
    changefreq = "monthly"

    def items(self):
        return ["home", "catalog:catalog-home", "about", "faq"]
    
    def location(self, item):
        return reverse(item)