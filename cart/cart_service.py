from django.db.models import F,Q,Count, Sum, FloatField
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from cart.models import CartItem, CartModel, Coupon
from catalog.models import ProductVariant, Product
import logging

logger = logging.getLogger(__name__)



def refresh_cart(cart):
    cart_exist = False
    if cart:
        logger.debug("refreshing Cart")
        cartitems = CartItem.objects.filter(cart=cart)
        cart_exist = cartitems.exists()
        if  cart_exist:
            aggregation = cartitems.aggregate(count=Sum('quantity'), total=Sum(F('quantity')*F('unit_price'), output_field=FloatField()))
            logger.debug("Cart Items agregation ready")
            CartModel.objects.filter(id=cart.id).update(quantity=aggregation['count'], amount=aggregation['total'])
            logger.debug("Cart updated")
            cart.refresh_from_db()
            logger.debug("Cart refreshed from db")
        else:
            logger.debug(f"No Cartitems found for user {cart.user.username}")
            CartModel.objects.filter(id=cart.id).update(quantity=0, amount=0)
    return cart, cart_exist

def get_cart(user=None):
    if not (isinstance(user, User)):
        logger.error(f"{user} is not an instance of User")
        return None
    cart = None
    try:
        cart = CartModel.objects.get(user=user)
    except CartModel.DoesNotExist:
        logger.warning(f"Cart not found for user {user.username}")
    return cart


def clear_cart(user=None):
    cart = get_cart(user)
    
    if user and cart and isinstance(user, User):
        logger.debug(f"Cart - Clearing cart for user {user.username}")
        num_of_deleted_objects, deleted_objects = CartItem.objects.filter(cart=cart).delete()
        logger.debug(f"Cart for user {user.username} has been clearded. {num_of_deleted_objects} Cartitems deleted")
        cart, cart_empty = refresh_cart(cart)
    return cart


def add_to_cart(cart, product_variant):
    """

    """
    if not (isinstance(cart, CartModel) and isinstance(product_variant, ProductVariant)):
        logger.error(f"type error : please verify the cart and product type")
        return None, False
    queryset = CartItem.objects.filter(cart=cart,product=product_variant)
    if queryset.exists():
        logger.info('Product already present in the cart.')
        cart_item = queryset.first()
        updated_rows, cart_sitem = update_cart(cart, cart_item, cart_item.quantity + 1)
        return cart_item, cart

    cart_item = CartItem.objects.create(cart=cart, product=product_variant, quantity=1, unit_price=product_variant.price, total_price=product_variant.price)
    refresh_cart(cart)
    logger.info('Product added into the cart')
    return cart_item, cart

def update_cart(cart, cart_item=None, quantity=1):
    """
    Update a product that is in the user cart.
    This method change the item quantity to the provided 
    quantity. 
    if quantity = 0 then the item will be removed from the cart.
    if quantity < 0 nothing is done.

    On success a boolean True is returned
    On fail a boolean False is returned
    """
    if not (isinstance(cart, CartModel) and isinstance(cart_item, CartItem)):
        return None, False
    if quantity == 0:
        return remove_from_cart(cart, cart_item)
    
    if quantity < 0:
        logger.warning('update_cart : quantity must be 0 or a positive number')
        return 0, False

    if quantity <= cart_item.product.quantity:
        updated_rows = CartItem.objects.filter(id=cart_item.id, is_active=True).update(quantity=quantity, total_price=F('unit_price') * quantity)
        cart_item.refresh_from_db()
        refresh_cart(cart)
        logger.info(f'update_cart : {updated_rows} row(s) in Cart Item updated quantity field to {quantity}')
        return updated_rows, cart_item

    else:
        if cart_item.product.quantity == 0 and cart_item.product.is_active:
            CartItem.objects.filter(id=cart_item.id).update(is_active=False)
        logger.warning('update_cart : The required quantity is not available')
        return -1, False

    return None, False


def remove_from_cart(cart, cart_item=None):
    deleted_count, delete_items = CartItem.objects.filter(id=cart_item.id, cart=cart).delete()
    refresh_cart(cart)
    return deleted_count, delete_items

def cart_items_count(user=None):
    if not (isinstance(user, User)):
        return -1
    
    #aggregation = CartItem.objects.filter(cart__user=user).aggregate(count=Sum('quantity'), total=Sum(F('quantity')*F('unit_price'), output_field=FloatField()))
    #CartModel.objects.filter(id=cart.id).update(quantity=aggregation['count'], amount=aggregation['total'])
    items_count = 0
    cart = get_cart(user)
    if cart:
        items_count = cart.quantity
        logger.debug(f"Cart Items Count : {items_count}")
    else:
        logger.debug(f"No Cart found for user {user.username} - Cart Items Count : {items_count}")
    return items_count


def get_cartitems(user):
    cart = get_cart(user)
    cartitems_queryset = None
    if cart:
        cartitems_queryset = CartItem.objects.filter(cart=cart)
    return cartitems_queryset

def apply_coupon(cart, coupon):
    if not isinstance(cart, CartModel) :
        return False
    if not isinstance(coupon, str):
        return False
    try:
        coupon_model = Coupon.objects.filter(name=coupon, is_active=True)
        price = cart.amount
        solded_price = price *((100 - coupon_model.reduction) / 100.0)
        CartModel.objects.filter(pk=cart.pk).update(coupon=coupon_model, solded_price=solded_price)
        logger.info(f"Coupon \"{coupon}\" applied to Cart for user \"{cart.user.username}\"")
    except ObjectDoesNotExist as e:
        logger.warn(f"No coupon found with the name \"{coupon}\"")
        logger.exception(e)
        return False
    return True
    