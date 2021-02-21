from django.utils.translation import gettext_lazy as _
from lyshop import settings

USER_RELATED_NAME = "wishlist"
ORDERING  = ["-created_at"]
WISHLIST_ITEM_RELATED_NAME = "wishlist_item"
WISHLIST_MANY_TO_MANY_RELATED_NAME = "wishlist_items"
WISHLIST_ITEM_FOREIGN_KEY = "catalog.Product"
USER_MAX_WISHLISTS = 5
HOME_TEMPLATE = "wishlist/wishlist_home.html"
WISHLIST_TEMPLATE = "wishlist/wishlist.html"
WISHLIST_CREATE_TEMPLATE = "wishlist/wishlist_create.html"
HOME_PAGE_TITLE = _("Wishlists") + "|" + settings.SITE_NAME