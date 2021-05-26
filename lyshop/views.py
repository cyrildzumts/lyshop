from django.shortcuts import render, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import auth
from django.templatetags.static import static
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.contrib.sitemaps import Sitemap
from catalog.models import Highlight, Category, Product
from catalog import constants as Catalog_Constants
# from django import forms
from django.contrib.auth.forms import UserCreationForm
from lyshop import settings, utils
from django.utils import timezone
import datetime

import logging

logger = logging.getLogger(__name__)

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
    new_arrivals = Product.objects.all()[:utils.MAX_RECENTS]
    soldes = Product.objects.filter(promotion_price__gt=0)[:utils.MAX_RECENTS]
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
    
    request.session['last_login'] = timezone.now().timestamp()
    
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
        'OG_URL': request.build_absolute_uri(),
        'new_arrivals': new_arrivals,
        'soldes': soldes,

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
    last_login = request.session.get('last_login')
    if last_login:
        d = datetime.datetime.fromtimestamp(last_login)
        logger.info(f'Last user login : {d}')
    else:
        logger.info(f'Last user login not set')
    
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


