from wishlist.models import Wishlist, WishlistItem
from django.utils.translation import gettext_lazy as _
from wishlist.forms import WishlistForm
from wishlist import constants
import logging

logger = logging.getLogger(__name__)

def get_wishlist(data):
    wishlist = Wishlist.objects.prefetch_related(constants.WISHLIST_MANY_TO_MANY_RELATED_NAME).filter(**data).get()
    return wishlist

def get_wishlists(data):
    return Wishlist.objects.filter(**data)


def create_wishlist(data):
    form = WishlistForm(data)
    w = None
    if form.is_valid():
        w = form.save()
        logger.info(f"Wishlist {w} created with data \"{data}\"." )
    else:
        logger.warn(f"Wishlist could not be created with data \"{data}\". Errors : {form.errors}" )
    return w


def update_wishlist(w, data):
    form = WishlistForm(data, instance=w)
    if form.is_valid():
        w = form.save()
        logger.info(f"Wishlist {w} updated with data \"{data}\"." )
    else:
        logger.warn(f"Wishlist could not be updated with data \"{data}\". Errors : {form.errors}" )
    return w


def delete_wishlist(w):
    if not isinstance(w, Wishlist):
        return
    Wishlist.objects.filter(pk=w.pk).delete()
    return

def delete_wishlists(id_list):
    if not isinstance(id_list, list)  or not len(id_list):
        return False

    wishlist_list = list(map(int, id_list))
    Wishlist.objects.filter(id__in=wishlist_list).delete()
    logger.info(f"Wishlists \"{wishlist_list}\" deleted")
    return True



def add_to_wishlist(w, product):
    if WishlistItem.objects.filter(product=product, wishlists__in=[w]).exists():
        logger.warn(f"Produc {product} already presents in wishlist {wishlist}")
        return False
    item, created = WishlistItem.objects.get_or_create(product=product)
    item.wishlists.add(w)
    return True


def remove_from_wishlist(w, product):
    if not WishlistItem.objects.filter(product=product, wishlists__in=[w]).exists():
        logger.warn(f"Produc {product} not presents in wishlist {wishlist}")
        return False

    item = WishlistItem.objects.get(product=product)
    item.wishlists.remove(w)
    return True

def wishlist_clear(wishlist):
    pass
