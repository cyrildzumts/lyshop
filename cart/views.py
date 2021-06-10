from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.http import HttpResponseBadRequest
from django.http import HttpResponse, JsonResponse
#from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_protect

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import F, Q, Count, Sum, FloatField
from lyshop import conf
from catalog.models import ProductVariant, Product
from cart.forms import CartItemForm, AddToCartForm, CartItemUpdateForm, AddCartForm, CouponForm, CartItemQuantityUpdateForm, CouponVerificationForm
from cart.models import CartItem, CartModel
from cart import cart_service
from core.resources import ui_strings as CORE_UI_STRINGS
from orders import orders_service
from catalog import catalog_service
from lyshop import settings, utils
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
    cart, cartitems_exist = cart_service.refresh_cart(cart)
    context = {
        'cart': cart,
        'cartitems_exist' : cartitems_exist,
        'payment_methods' : orders_service.get_payment_methods(filter_active=True),
        'item_list' : CartItem.objects.select_related('product').prefetch_related('product__attributes').filter(cart=cart),
        'page_title' : settings.SITE_NAME + ' ' + 'Cart',
    }

    return render(request, template_name, context)


@login_required
def add_to_cart_old(request):
    cart, created = CartModel.objects.get_or_create(user=request.user)
    context = {
        'success': False
    }
    logger.debug("ajax-add-to-cart")
    if request.method == 'POST':
        postdata = request.POST.copy()
        form = AddToCartForm(postdata)
        if form.is_valid():
            product = form.cleaned_data['product']
            result , cart = cart_service.add_to_cart(cart, product)
            if result:
                context['success'] = True
                context['status'] = True
                #return redirect(product.get_absolute_url())
        else:
            context['error'] = 'Form is invalid'
            context['status'] = False
            messages.error(request, message="Invalid Form")
            #if request.is_ajax():
            #   return JsonResponse(context,status=HTTPStatus.BAD_REQUEST)
            
    else:
        context['error'] = 'Bad Request'
        context['status'] = False
        return redirect('catalog:home')

    
@login_required
def add_to_cart(request):
    cart, created = CartModel.objects.get_or_create(user=request.user)
    context = {
        'success': False
    }
    if request.method == 'POST':
        postdata = request.POST.copy()
        result = cart_service.add_product_to_cart(request.user, postdata)
        if result['status']:
            messages.success(request, message=_(CORE_UI_STRINGS.PRODUCT_ADDED))
            return redirect(result['product_url'])
        else:
            context['error'] = CORE_UI_STRINGS.INVALID_FORM
            context['status'] = False
            messages.error(request, message=_(CORE_UI_STRINGS.INVALID_FORM))
            
    else:
        context['error'] = 'Bad Request'
        context['status'] = False
        return redirect('catalog:home')


@login_required
def ajax_add_coupon(request):
    cart, created = CartModel.objects.get_or_create(user=request.user)
    context = {
        'success' : False,
        'status' : False,
    }
    if request.method == 'POST':
        postdata = request.POST.copy()
        #coupon = postdata.get('name')
        #coupon_applied = cart_service.apply_coupon(cart, coupon)
        coupon_applied, context = cart_service.process_apply_coupon(request.user, postdata)
        cart.refresh_from_db()
        return JsonResponse(context)
    else:
        context['error'] = 'Method not allowed. POST requets expected.'
        return JsonResponse(context, status=HTTPStatus.METHOD_NOT_ALLOWED)


@login_required
def ajax_add_to_cart_old(request):
    cart, created = CartModel.objects.get_or_create(user=request.user)
    context = {
        'success': False
    }
    if request.method == 'POST':
        postdata = request.POST.copy()

        form = AddCartForm(postdata)
        if form.is_valid():
            logger.debug("Summitted data are valid")
            variant_uuid = form.cleaned_data['variant_uuid']
            attr = form.cleaned_data['attr']
            variant = get_object_or_404(ProductVariant, product_uuid=variant_uuid)
            result, cart = cart_service.add_to_cart(cart, variant)
            prefix = variant.product.display_name
            if result:
                cart.refresh_from_db()
                context['success'] = True
                context['status'] = True
                context['quantity'] = cart.quantity
                context['message'] =  _(CORE_UI_STRINGS.PRODUCT_ADDED)
                return JsonResponse(context)
            else:
                context['success'] = False
                context['status'] = True
                context['quantity'] = cart.quantity
                context['message'] =  _(CORE_UI_STRINGS.PRODUCT_QTY_NOT_AVAILABLE)
                return JsonResponse(context)


        else:
            logger.error(f"Form is invalid. {form.errors}")
            context['error'] = _(CORE_UI_STRINGS.INVALID_FORM)
            context['status'] = False
            return JsonResponse(context,status=HTTPStatus.BAD_REQUEST)
            
    else:
        logger.warn("Ajax send as GET Request")
    context['error'] = 'Bad Request'
    context['status'] = False
    return JsonResponse(context, status=HTTPStatus.BAD_REQUEST)


@login_required
def ajax_add_to_cart(request):
    cart, created = CartModel.objects.get_or_create(user=request.user)
    context = {
        'success': False
    }
    if request.method == 'POST':
        postdata = request.POST.copy()
        result = cart_service.add_product_to_cart(request.user, postdata)
        if result['success']:
            cart.refresh_from_db()
            context['success'] = True
            context['status'] = True
            context['quantity'] = cart.quantity
            context['message'] =  _(CORE_UI_STRINGS.PRODUCT_ADDED)
            return JsonResponse(context)
        else:
            context['success'] = False
            context['status'] = True
            context['quantity'] = cart.quantity
            context['message'] =  _(CORE_UI_STRINGS.PRODUCT_QTY_NOT_AVAILABLE)
            return JsonResponse(context)
            
    else:
        logger.warn("Ajax send as GET Request")
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
        context['cart_total'] = float(f'{cart.amount:g}')
        context['subtotal'] = float(f'{cart.amount:g}')
        context['total'] = float(f'{cart.get_total():g}')
        context['reduction'] = float(f'{cart.get_reduction():g}')
        context['count'] = cart.quantity

        return JsonResponse(context, status=HTTPStatus.NOT_ACCEPTABLE)
    
      

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
        context['cart_total'] = float(f'{cart.amount:g}')
        context['subtotal'] = float(f'{cart.amount:g}')
        context['total'] = float(f'{cart.get_total():g}')
        context['reduction'] = float(f'{cart.get_reduction():g}')
        context['count'] = cart.quantity

        return JsonResponse(context)




@login_required
def ajax_cart_item_update_quantity(request):
    logger.info(f"Ajax Cart item update requested by User \"{request.user}\"")
    cart, created = CartModel.objects.get_or_create(user=request.user)
    item = None
    context = {
        'success' : False
    }
    if request.method != 'POST':
        context['error'] = 'Method not allowed. POST requets expected.'
        context['status'] = False
        return JsonResponse(context, status=HTTPStatus.METHOD_NOT_ALLOWED)

    form = CartItemQuantityUpdateForm(utils.get_postdata(request))
    if not form.is_valid():
        context['error'] = 'Invalid Form'
        context['status'] = False
        logger.error(f"Cart item update quantity : Form error  \"{form.errors}\"")
        return JsonResponse(context, status=HTTPStatus.BAD_REQUEST)
    try:
        item = CartItem.objects.filter(item_uuid=form.cleaned_data.get('item_uuid')).select_related().get()
    except CartItem.DoesNotExist as e:
        context['error'] = 'No Cart Item found.'
        context['status'] = False
        logger.info(f"Cart item update quantity : Cart Item not found.")
        return JsonResponse(context, status=HTTPStatus.NOT_FOUND)

    requested_quantity = form.cleaned_data.get('quantity')
    updated_rows , item = cart_service.update_cart(cart, item, requested_quantity)
    
    if updated_rows == -1 :
        context['error'] = f'Requested quantity \"{requested_quantity}\" not available.'
        context['item_quantity'] = item.quantity
        context['status'] = False
        context['is_active'] = True
        logger.info(f"Cart item update quantity : Requested quantity \"{requested_quantity}\" not available.")
        return JsonResponse(context, status=HTTPStatus.NOT_ACCEPTABLE)
    
    if updated_rows == 0:
        context['error'] = f'invalid quantity \"{requested_quantity}\" received.'
        context['item_quantity'] = item.quantity
        context['status'] = False
        context['is_active'] = True
        logger.error(f'invalid quantity \"{requested_quantity}\" received.')
        return JsonResponse(context, status=HTTPStatus.NOT_ACCEPTABLE)

    if updated_rows == 1:
        cart.refresh_from_db()
        item.refresh_from_db()
        context['success'] = True
        context['status'] = True
        context['item_quantity'] = requested_quantity
        context['item_total'] = item.total_price
        context['total'] = float(f'{cart.amount:g}')
        context['solded_price'] = float(f'{cart.solded_price:g}')
        context['reduction'] = float(f'{cart.get_reduction():g}')
        context['subtotal'] = float(f'{cart.amount:g}')
        context['total'] = float(f'{cart.get_total():g}')
        context['cart_quantity'] = cart.quantity
        logger.info(f"Updated  Cart Item  \"{item}\" quantity from Cart \"{cart}\" to quantity {item.quantity}")
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
        context['cart_total'] = float(f'{cart.amount:g}')
        context['subtotal'] = float(f'{cart.amount:g}')
        context['total'] = float(f'{cart.get_total():g}')
        context['reduction'] = float(f'{cart.get_reduction():g}')
        context['count'] = cart.quantity
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
    
    cart_service.remove_from_cart(cart, item)
    cart.refresh_from_db()
    context['success'] = True
    context['status'] = True
    context['cart_total'] = float(f'{cart.amount:g}')
    context['count'] = cart.quantity
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
        logger.debug(f"ajax_cart_item_update : REQUEST.METHOD : {request.method}")
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
            context['item_total'] = float(f'{item.item_total_price:g}')
            context['removed'] = False
        else:
            context['removed'] = True
        context['cart_total'] = float(f'{cart.amount:g}')
        context['subtotal'] = float(f'{cart.amount:g}')
        context['total'] = float(f'{cart.get_total():g}')
        context['reduction'] = float(f'{cart.get_reduction():g}')
        context['count'] = cart.quantity
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


@login_required
def ajax_debug(request):
    context = {
        'path' : request.path,
        'method' : request.method,
        'encoding' : request.encoding,
        'content_type': request.content_type,
        'cookies' : request.COOKIES,
        'GET' : request.GET,
        'POST': request.POST,
        'scheme': request.scheme
    }
    return JsonResponse(context)

@login_required
def ajax_coupon_verify(request):
    context = {
        'success' : False
    }
    if request.method == 'POST':
        valid = cart_service.is_valid_coupon(request.POST.copy())
        context['success'] = True
        context['status'] = True
        context['valid'] = valid
        return JsonResponse(context)

    context['status'] = False
    context['error'] = 'Bad Request'
    return JsonResponse(context, status=HTTPStatus.BAD_REQUEST)


@login_required
def ajax_coupon_remove(request):
    context = {
        'success' : False
    }
    cart, created = CartModel.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        removed, context = cart_service.remove_coupon(request.user, request.POST.copy())
        return JsonResponse(context)

    context['status'] = False
    context['error'] = 'Bad Request'
    return JsonResponse(context, status=HTTPStatus.BAD_REQUEST)