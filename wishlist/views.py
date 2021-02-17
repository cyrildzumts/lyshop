from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponseBadRequest
from django.http import HttpResponse, JsonResponse
from http import HTTPStatus
from wishlist import wishlist_service
from wishlist import constants
from wishlist.models import Wishlist, WishlistItem
from catalog.models import Product
from wishlist.forms import WishlistForm, AddToWishlistForm, CreateAndAddWishlistForm, RenameWishlistForm
from lyshop import utils, settings, conf as GLOBAL_CONF
import logging

logger = logging.getLogger(__name__)

# Create your views here.
@login_required
def wishlist_home(request):
    template_name = constants.HOME_TEMPLATE
    queryset = wishlist_service.get_wishlists({'customer': request.user})
    context = {
        'page_title' : constants.HOME_PAGE_TITLE,
        'queryset' : queryset,
        'wishlist_list': queryset
    }

    return render(request, template_name, context)

@login_required
def wishlist(request, wishlist_uuid):
    template_name = constants.WISHLIST_TEMPLATE
    if request.method != "GET":
        raise SuspiciousOperation('Bad request')

    w = get_object_or_404(Wishlist, customer=request.user, wishlist_uuid=wishlist_uuid)
    items = w.wishlist_items.all()
    context = {
        'page_title' : w.name + "|" + settings.SITE_NAME,
        'wishlist' : w,
        'queryset' : items,
        'wishlist_items' : items
    }
    return render(request, template_name, context)


@login_required
def wishlist_update(request, wishlist_uuid=None):
    username = request.user.username
    template_name = 'wishlist/wishlist_update.html'
    page_title = _('Wishlist Update')
    
    form = None
    w = get_object_or_404(Wishlist, customer=request.user, wishlist_uuid=wishlist_uuid)
    old_name = w.name
    if request.method == 'POST':
        postdata = utils.get_postdata(request)
        w = wishlist_service.update_wishlist(w, postdata)
        messages.success(request, _('Shopping list updated'))
        logger.info(f'Wishlist {old_name} updated to {w.name} by user \"{username}\"')
        return redirect('wishlist:wishlist', wishlist_uuid=wishlist_uuid)
    else:
        form = WishlistForm(instance=w)
    context = {
        'page_title': page_title,
        'form' : form,
        'wishlist': w
    }
    return render(request, template_name, context)


@login_required
def wishlists_delete(request):
    username = request.user.username

    if request.method != "POST":
        raise SuspiciousOperation('Bad request. Expected POST request but received a GET')
    
    postdata = utils.get_postdata(request)
    id_list = postdata.getlist('wishlists')
    deleted = wishlist_service.delete_wishlists(id_list)
    if deleted:
        messages.success(request, f"Shopping List  deleted")
    else:
        messages.error(request, f"Shopping List could not be deleted")
        logger.error(f"ID list invalid. Error : {id_list}")
    return redirect('wishlist:wishlist-home')


@login_required
def wishlist_create(request):
    username = request.user.username
    template_name = 'wishlist/wishlist_create.html'
    page_title = _('Shopping List')
    form = None
    if request.method == 'POST':
        postdata = utils.get_postdata(request)
        w = wishlist_service.create_wishlist(postdata)
        if w is not None:
            messages.success(request, _('Shopping list created'))
            logger.info(f'Wishlist {w.name} created by user \"{username}\"')
            return redirect('wishlist:wishlist-home')
        else:
            messages.warning(request, _('Shopping list not created'))
            logger.warn(f'Wishlist not created by user \"{username}\"')
            return redirect('wishlist:wishlist-home')
    else:
        form = WishlistForm()
    context = {
        'page_title': page_title,
        'form' : form
    }
    return render(request, template_name, context)


@login_required
def wishlist_clear(request, wishlist_uuid):
    pass


@login_required
def wishlist_add(request, wishlist_uuid, product_uuid):
    if request.method != "POST":
        messages.add_message(request, messages.WARNING, "BAD REQUEST")
        return redirect("catalog:catalog-home")
    w = get_object_or_404(Wishlist, customer=request.user, wishlist_uuid=wishlist_uuid)
    p = get_object_or_404(Product, product_uuid=product_uuid)
    next_url = request.POST.copy().get('next_url')
    added = wishlist_service.add_to_wishlist(w, p)

    return redirect(next_url)

@login_required
def wishlist_ajax_add(request):
    context = {}
    if request.method != "POST":
        context['error'] = 'Bad Request. POST method required'
        context['status'] = False
        return JsonResponse(context,status=HTTPStatus.BAD_REQUEST)
    
    
    form = AddToWishlistForm(utils.get_postdata(request))
    if form.is_valid():
        wishlist_uuid = form.cleaned_data.get('wishlist_uuid')
        product_uuid = form.cleaned_data.get('product_uuid')
        w = get_object_or_404(Wishlist, customer=request.user, wishlist_uuid=wishlist_uuid)
        p = get_object_or_404(Product, product_uuid=product_uuid)
        added = wishlist_service.add_to_wishlist(w, p)
        if added:
                prefix = p.display_name 
                context['success'] = True
                context['status'] = True
                context['quantity'] = WishlistItem.objects.filter(wishlists__in=[w]).count()
                context['message'] =  prefix + " " + str(_('added to list')) + w.name
                return JsonResponse(context)
        else:
            logger.error(f"Form is invalid. {form.errors}")
            context['error'] = 'Bad Request. product missing'
            context['status'] = False
            return JsonResponse(context,status=HTTPStatus.BAD_REQUEST)
    
    context['error'] = 'Bad Request. submitted data invalid'
    context['status'] = False
    return JsonResponse(context,status=HTTPStatus.BAD_REQUEST)


@login_required
def wishlist_ajax_remove(request):
    context = {}
    if request.method != "POST":
        context['error'] = 'Bad Request. POST method required'
        context['status'] = False
        return JsonResponse(context,status=HTTPStatus.BAD_REQUEST)
    
    
    form = AddToWishlistForm(utils.get_postdata(request))
    if form.is_valid():
        wishlist_uuid = form.cleaned_data.get('wishlist_uuid')
        product_uuid = form.cleaned_data.get('product_uuid')
        w = get_object_or_404(Wishlist, customer=request.user, wishlist_uuid=wishlist_uuid)
        p = get_object_or_404(Product, product_uuid=product_uuid)
        removed = wishlist_service.remove_from_wishlist(w, p)
        if removed:
                prefix = p.display_name 
                context['success'] = True
                context['status'] = True
                context['quantity'] = WishlistItem.objects.filter(wishlists__in=[w]).count()
                context['message'] =  prefix + " " + str(_('removed from list ')) + w.name
                return JsonResponse(context)
        else:
            logger.error(f"Form is invalid. {form.errors}")
            context['error'] = 'Bad Request. product missing'
            context['status'] = False
            return JsonResponse(context,status=HTTPStatus.BAD_REQUEST)
    
    context['error'] = 'Bad Request. submitted data invalid'
    context['status'] = False
    return JsonResponse(context,status=HTTPStatus.BAD_REQUEST)

@login_required
def wishlist_ajax_create_add(request):
    context = {}
    if request.method != "POST":
        context['error'] = 'Bad Request. POST method required'
        context['status'] = False
        return JsonResponse(context,status=HTTPStatus.BAD_REQUEST)
    
    
    form = CreateAndAddWishlistForm(utils.get_postdata(request))
    if form.is_valid():
        name = form.cleaned_data.get('name')
        product_uuid = form.cleaned_data.get('product_uuid')
        customer = User.objects.get(pk=form.cleaned_data.get('customer'))

        w = wishlist_service.create_wishlist({'name': name, 'customer': customer})
        p = get_object_or_404(Product, form.cleaned_data.get('product_uuid'))
        added = wishlist_service.add_to_wishlist(w, p)
        if added:
                prefix = p.display_name 
                context['success'] = True
                context['wishlist'] = w.name
                context['status'] = True
                context['message'] =  prefix + " " + str(_('added to list')) + w.name
                return JsonResponse(context)
        else:
            logger.error(f"Form is invalid. {form.errors}")
            context['error'] = 'Bad Request. product missing'
            context['status'] = False
            return JsonResponse(context,status=HTTPStatus.BAD_REQUEST)
    logger.warning(f"Wishlist creation errors : {form.errors}")
    context['error'] = 'Bad Request. submitted data invalid'
    context['status'] = False
    return JsonResponse(context,status=HTTPStatus.BAD_REQUEST)

@login_required
def wishlist_ajax_rename(request):
    context = {}
    if request.method != "POST":
        context['error'] = 'Bad Request. POST method required'
        context['status'] = False
        return JsonResponse(context,status=HTTPStatus.BAD_REQUEST)
    
    form = RenameWishlistForm(utils.get_postdata(request))
    if form.is_valid():
        name = form.cleaned_data.get('name')
        wishlist_uuid = form.cleaned_data.get('wishlist_uuid')
        customer = User.objects.get(pk=form.cleaned_data.get('customer'))
        w = get_object_or_404(Wishlist, customer=customer, wishlist_uuid=wishlist_uuid)
        updated = wishlist_service.update_wishlist(w, {'name' : form.cleaned_data.get('name'), 'customer': customer })
        if updated:
                prefix = w.name
                context['success'] = True
                context['status'] = True
                context['message'] =  prefix + " " + str(_('shop list renamed to')) + name
                return JsonResponse(context)
        else:
            logger.error(f"Form is invalid. {form.errors}")
            context['error'] = 'Bad Request.'
            context['status'] = False
            return JsonResponse(context,status=HTTPStatus.BAD_REQUEST)
    
    context['error'] = 'Bad Request. submitted data invalid'
    context['status'] = False
    return JsonResponse(context,status=HTTPStatus.BAD_REQUEST)

@login_required
def wishlist_remove(request, wishlist_uuid, product_uuid):
    if request.method != "POST":
        messages.add_message(request, messages.WARNING, "BAD REQUEST")
        return redirect("catalog:catalog-home")
    w = get_object_or_404(Wishlist, customer=request.user, wishlist_uuid=wishlist_uuid)
    p = get_object_or_404(Product, product_uuid=product_uuid)
    next_url = request.POST.copy().get('next_url')
    added = wishlist_service.remove_from_wishlist(w, p)
    return redirect(next_url)


@login_required
def wishlist_delete(request, wishlist_uuid):
    if request.method != "POST":
        messages.add_message(request, messages.WARNING, "BAD REQUEST")
        return redirect("catalog:catalog-home")
    w = get_object_or_404(Wishlist, customer=request.user, wishlist_uuid=wishlist_uuid)
    wishlist_service.delete_wishlist(w)
    return redirect("wishlist:wishlist-home")

@login_required
def wishlist_move_to_cart(request, wishlist_uuid):
    pass



