from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from wishlist import wishlist_service
from wishlist import constants
from wishlist.forms import WishlistForm
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
    template_name = constants.HOME_TEMPLATE
    if request.method != "GET":
        raise SuspiciousOperation('Bad request')

    w = get_object_or_404('wishlist.Wishlist', customer=request.user, wishlist_uuid=wishlist_uuid)
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
    w = get_object_or_404('wishlist.Wishlist', customer=request.user, wishlist_uuid=wishlist_uuid)
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
            messages.warn(request, _('Shopping list not created'))
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
    w = get_object_or_404('wishlist.Wishlist', customer=request.user, wishlist_uuid=wishlist_uuid)
    p = get_object_or_404('catalog.Product', product_uuid=product_uuid)
    next_url = request.POST.copy().get('next_url')
    added = wishlist_service.add_to_wishlist(w, p)
    return redirect(next_url)


@login_required
def wishlist_remove(request, wishlist_uuid, product_uuid):
    if request.method != "POST":
        messages.add_message(request, messages.WARNING, "BAD REQUEST")
        return redirect("catalog:catalog-home")
    w = get_object_or_404('wishlist.Wishlist', customer=request.user, wishlist_uuid=wishlist_uuid)
    p = get_object_or_404('catalog.Product', product_uuid=product_uuid)
    next_url = request.POST.copy().get('next_url')
    added = wishlist_service.remove_from_wishlist(w, p)
    return redirect(next_url)


@login_required
def wishlist_delete(request, wishlist_uuid):
    if request.method != "POST":
        messages.add_message(request, messages.WARNING, "BAD REQUEST")
        return redirect("catalog:catalog-home")
    w = get_object_or_404('wishlist.Wishlist', customer=request.user, wishlist_uuid=wishlist_uuid)
    wishlist_service.delete_wishlist(w)
    return redirect("wishlist:wishlist-home")

@login_required
def wishlist_move_to_cart(request, wishlist_uuid):
    pass



