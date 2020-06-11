from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.http import HttpResponseBadRequest
from django.http import HttpResponse, JsonResponse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import F, Q, Count, Sum, FloatField
from catalog import conf
from catalog.models import ProductVariant, Product
from cart.forms import CartItemForm, AddToCartForm, CartItemUpdateForm, AddCartForm
from cart.models import CartItem, CartModel
from cart import cart_service
from catalog import catalog_service
from lyshop import settings
from http import HTTPStatus
import json
import logging
import uuid

logger = logging.getLogger(__name__)

# Create your views here.

@login_required
def cart(request):
    cart, created = CartModel.objects.get_or_create(user=request.user)
    template_name = 'cart/cart.html'
    if request.method == 'POST':
        pass
    cart, cart_empty = cart_service.refresh_cart(cart)
    context = {
        'cart': cart,
        'cart_empty' : cart_empty,
        'item_list' : CartItem.objects.filter(cart=cart),
        'page_title' : _("Shopping Cart") + ' - ' + settings.SITE_NAME
    }

    return render(request, template_name, context)


@login_required
def add_to_cart(request):
    cart, created = CartModel.objects.get_or_create(user=request.user)
    context = {
        'success': False
    }
    if request.method == 'POST':
        postdata = request.POST.copy()
        form = AddToCartForm(postdata)
        if form.is_valid():
            product = form.cleaned_data['product']
            result = cart_service.add_to_cart(cart, product)
            if result:
                context['success'] = True
                context['status'] = True
                return redirect(product.get_absolute_url())
        else:
            context['error'] = 'Bad Request. product_uuid missing'
            context['status'] = False
            if request.is_ajax():
                return JsonResponse(context,status=HTTPStatus.BAD_REQUEST)
            
    else:
        context['error'] = 'Bad Request'
        context['status'] = False
        return redirect('catalog:home')

@login_required
def ajax_add_to_cart(request):
    cart, created = CartModel.objects.get_or_create(user=request.user)
    context = {
        'success': False
    }
    logger.debug("ajax-add-to-cart")
    if request.method == 'POST':
        postdata = request.POST.copy()

        form = AddCartForm(postdata)
        if form.is_valid():
            logger.debug("Summitted data are valid")
            variant_uuid = form.cleaned_data['variant_uuid']
            attr = form.cleaned_data['attr']
            variant = get_object_or_404(ProductVariant, product_uuid=variant_uuid)
            result = cart_service.add_to_cart(cart, variant)
            if result:
                context['success'] = True
                context['status'] = True
                return JsonResponse(context)

        else:
            logger.error(f"Form is invalid. {form.errors}")
            context['error'] = 'Bad Request. product missing'
            context['status'] = False
            return JsonResponse(context,status=HTTPStatus.BAD_REQUEST)
            
    
    context['error'] = 'Bad Request'
    context['status'] = False
    return JsonResponse(context, status=HTTPStatus.BAD_REQUEST)


@login_required
def ajax_cart_item_increment(request, item_uuid):
    cart, created = CartModel.objects.get_or_create(user=request.user)
    item = None
    context = {
        'success' : False
    }
    if request.method != 'POST':
        context['error'] = 'Method not allowed. POST requets expected.'
        context['status'] = False
        return JsonResponse(context, status=HTTPStatus.METHOD_NOT_ALLOWED)
    
    try:
        item = CartItem.objects.filter(item_uuid=item_uuid).select_related().get()
    except CartItem.DoesNotExist as e:
        context['error'] = 'No Cart Item found.'
        context['status'] = False
        return JsonResponse(context, status=HTTPStatus.NOT_FOUND)


    item_quantity = item.quantity
    requested_quantity = item_quantity + 1
    updated_rows , item = cart_service.update_cart(cart, item,requested_quantity)
    cart.refresh_from_db()
    if updated_rows == -1 :
        context['error'] = f'Requested quantity \"{requested_quantity}\" not available.'
        context['status'] = False
        context['is_active'] = True
            
        return JsonResponse(context, status=HTTPStatus.NOT_ACCEPTABLE)
    
    if updated_rows == 0:
        context['error'] = f'invalid quantity \"{requested_quantity}\" received.'
        context['status'] = False
        context['is_active'] = True
            
        return JsonResponse(context, status=HTTPStatus.NOT_ACCEPTABLE)

    if updated_rows == 1:
        context['success'] = True
        context['status'] = True
        context['item_quantity'] = item.quantity
        context['item_total'] = item.total_price
        context['cart_total'] = cart.amount
        context['cart_quantity'] = cart.quantity

        return JsonResponse(context)
    
      

@login_required
def ajax_cart_item_decrement(request, item_uuid):
    cart, created = CartModel.objects.get_or_create(user=request.user)
    item = None
    context = {
        'success' : False
    }
    if request.method != 'POST':
        context['error'] = 'Method not allowed. POST requets expected.'
        context['status'] = False
        return JsonResponse(context, status=HTTPStatus.METHOD_NOT_ALLOWED)
    
    try:
        item = CartItem.objects.filter(item_uuid=item_uuid).select_related().get()
    except CartItem.DoesNotExist as e:
        context['error'] = 'No Cart Item found.'
        context['status'] = False
        return JsonResponse(context, status=HTTPStatus.NOT_FOUND)


    item_quantity = item.quantity
    requested_quantity = item_quantity - 1
    updated_rows , item = cart_service.update_cart(cart, item,requested_quantity)
    cart.refresh_from_db()
    if updated_rows == -1 :
        context['error'] = f'Requested quantity \"{requested_quantity}\" not available.'
        context['status'] = False
        context['is_active'] = True
            
        return JsonResponse(context, status=HTTPStatus.NOT_ACCEPTABLE)
    
    if updated_rows == 0:
        context['error'] = f'invalid quantity \"{requested_quantity}\" received.'
        context['status'] = False
        context['is_active'] = True
            
        return JsonResponse(context, status=HTTPStatus.NOT_ACCEPTABLE)

    if updated_rows == 1:
        context['success'] = True
        context['status'] = True
        context['item_quantity'] = item.quantity
        context['item_total'] = item.total_price
        context['cart_total'] = cart.amount
        context['cart_quantity'] = cart.quantity

        return JsonResponse(context)


@login_required
def ajax_cart_item_delete(request, item_uuid):
    cart, created = CartModel.objects.get_or_create(user=request.user)
    item = None
    context = {
        'success' : False
    }
    if request.method != 'POST':
        context['error'] = 'Method not allowed. POST requets expected.'
        context['status'] = False
        return JsonResponse(context, status=HTTPStatus.METHOD_NOT_ALLOWED)

    deleted_rows, deleted_items = CartItem.objects.filter(item_uuid=item_uuid).delete()
    cart, cart_empty = cart_service.refresh_cart(cart)
    if deleted_rows == 1:
        context['success'] = True
        context['status'] = True
        context['cart_empty'] = cart_empty
        context['cart_total'] = cart.amount
        context['cart_quantity'] = cart.quantity
        return JsonResponse(context)
    else :
        context['error'] = 'No Cart Item found.'
        context['status'] = False
        return JsonResponse(context, status=HTTPStatus.NOT_FOUND)
        

@login_required
def ajax_cart_item_to_wishlist(request, item_uuid):
    logger.info('Adding Cart Item with uuid \"{item_uuid}\" into wishlist')
    context = {
        'success' : False
    }
    cart, created = CartModel.objects.get_or_create(user=request.user)
    try:
        item = CartItem.objects.filter(item_uuid=item_uuid).select_related().get()
    except CartItem.DoesNotExist as e:
        context['error'] = 'No Cart Item found.'
        context['status'] = False
        return JsonResponse(context, status=HTTPStatus.NOT_FOUND)
    
    product = item.product
    cart_service.remove_from_cart(cart, item)
    cart.refresh_from_db()
    context['success'] = True
    context['status'] = True
    context['cart_total'] = cart.amount
    context['cart_quantity'] = cart.quantity
    return JsonResponse(context)
    


@login_required
def ajax_cart_item_update(request, item_uuid=None, action=None):
    logger.info(f"Cart Item Update Ajax : item \"{item_uuid}\" - action \"{action}\"")
    cart, created = CartModel.objects.get_or_create(user=request.user)
    item = None
    context = {
        'success' : False
    }
    if request.method != 'POST':
        context['error'] = 'Method not allowed. POST requets expected.'
        context['status'] = False
        logger.warn(context['error'])
        return JsonResponse(context, status=HTTPStatus.METHOD_NOT_ALLOWED)
    
    try:
        item = CartItem.objects.filter(item_uuid=item_uuid).select_related().get()
    except CartItem.DoesNotExist as e:
        context['error'] = 'No Cart Item found.'
        context['status'] = False
        logger.warn(context['error'])
        return JsonResponse(context, status=HTTPStatus.NOT_FOUND)


    item_quantity = item.quantity
    requested_quantity = item_quantity + 1 if action=='increment' else item_quantity - 1
    if action == 'increment':
        requested_quantity = item_quantity + 1
    elif action == 'decrement':
        requested_quantity = item_quantity - 1
    elif action == 'delete':
        requested_quantity = 0
    
    else :
        context['error'] = f'Bad request. Unknown request action \"{action}\"'
        context['status'] = False
        logger.warn(context['error'])
        return JsonResponse(context, status=HTTPStatus.BAD_REQUEST)
    
    updated_rows , item = cart_service.update_cart(cart, item,requested_quantity)
    cart.refresh_from_db()
    if updated_rows == -1 :
        context['error'] = f'Requested quantity \"{requested_quantity}\" not available.'
        context['status'] = False
        context['is_active'] = True
        logger.warn(context['error'])
        return JsonResponse(context, status=HTTPStatus.NOT_ACCEPTABLE)
    
    if updated_rows == 0:
        context['error'] = f'invalid quantity \"{requested_quantity}\" received.'
        context['status'] = False
        context['is_active'] = True
        logger.warn(context['error'])
        return JsonResponse(context, status=HTTPStatus.NOT_ACCEPTABLE)

    if updated_rows == 1:
        context['success'] = True
        context['status'] = True
        if requested_quantity > 0:
            context['item_quantity'] = item.quantity
            context['item_total'] = item.total_price
            context['removed'] = False
        else:
            context['removed'] = True
        context['cart_total'] = cart.amount
        context['cart_quantity'] = cart.quantity
        logger.info(f'Cart Item \"{item_uuid}\" updated by user \"{request.user}\""')
        return JsonResponse(context)
    

@login_required
def cart_update(request, item_uuid):
    cart, created = CartModel.objects.get_or_create(user=request.user)
    item = get_object_or_404(CartItem, item_uuid=item_uuid)
    context = {
        'success' : False
    }
    if request.method == 'POST':
        form = CartItemUpdateForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            result = cart_service.update_cart(cart, item, quantity)
            updated, updated_item = result
            context['success'] = True
            context['status'] = True
            context['quantity'] = updated_item.quantity
            return JsonResponse(context)

        else:
            context['status'] = False
            context['error'] = 'Bad Request. quantity is missing'
            return JsonResponse(context, status=HTTPStatus.BAD_REQUEST)
    context['status'] = False
    context['error'] = 'Bad Request'
    return JsonResponse(context, status=HTTPStatus.BAD_REQUEST)


@login_required
def cart_clear(request):
    cart, created = CartModel.objects.get_or_create(user=request.user)
    CartItem.objects.filter(cart=cart).delete()
    context = {
        'success' : True,
        'status' : True
    }
    return JsonResponse(context)