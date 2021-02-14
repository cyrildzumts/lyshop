from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from wishlist import wishlist_service
from wishlist import constants
from lyshop import utils, settings, conf as GLOBAL_CONF


# Create your views here.

def wishlist_home(request):
    template_name = constants.HOME_TEMPLATE
    queryset = wishlist_service.get_wishlists({'customer': request.user})
    context = {
        'page_title' : constants.HOME_PAGE_TITLE,
        'queryset' : queryset,
        'wishlist_list': queryset
    }

    return render(request, template_name, context)

def wishlist(request, wishlist_uuid):
    template_name = constants.HOME_TEMPLATE
    w = get_object_or_404('wishlist.Wishlist', customer=request.user, wishlist_uuid=wishlist_uuid)
    items = w.wishlist_items.all()
    context = {
        'page_title' : w.name + "|" + settings.SITE_NAME,
        'wishlist' : w,
        'queryset' : items,
        'wishlist_items' : items
    }

    return render(request, template_name, context)

def wishlist_clear(request, wishlist_uuid):
    pass



def wishlist_add(request, wishlist_uuid, product_uuid):
    if request.method != "POST":
        messages.add_message(request, messages.WARNING, "BAD REQUEST")
        return redirect("catalog:catalog-home")
    w = get_object_or_404('wishlist.Wishlist', customer=request.user, wishlist_uuid=wishlist_uuid)
    p = get_object_or_404('catalog.Product', product_uuid=product_uuid)
    next_url = request.POST.copy().get('next')
    added = wishlist_service.add_to_wishlist(w, p)
    return redirect(next_url)



def wishlist_remove(request, wishlist_uuid, product_uuid):
    if request.method != "POST":
        messages.add_message(request, messages.WARNING, "BAD REQUEST")
        return redirect("catalog:catalog-home")
    w = get_object_or_404('wishlist.Wishlist', customer=request.user, wishlist_uuid=wishlist_uuid)
    p = get_object_or_404('catalog.Product', product_uuid=product_uuid)
    next_url = request.POST.copy().get('next')
    added = wishlist_service.remove_from_wishlist(w, p)
    return redirect(next_url)


def wishlist_move_to_cart(request, wishlist_uuid):
    pass



