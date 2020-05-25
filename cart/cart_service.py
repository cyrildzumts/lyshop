from django.db.models import F,Q,Count, Sum, FloatField
from django.contrib.auth.models import User
from cart.models import CartItem, CartModel
from catalog.models import ProductVariant, Product
import logging

logger = logging.getLogger(__name__)



def refresh_cart(cart):
    if cart:
        aggregation = CartItem.objects.filter(cart=cart).aggregate(count=Sum('quantity'), total=Sum(F('quantity')*F('unit_price'), output_field=FloatField()))
        CartModel.objects.filter(id=cart.id).update(quantity=aggregation['count'], amount=aggregation['total'])
        cart.refresh_from_db()
    
    return cart

def get_cart(user=None):
    if not (isinstance(user, User)):
        logger.error(f"{user} is not an instance of User")
        return None

    try:
        cart = CartModel.objects.get(user=user)
    except CartModel.DoesNotExist:
        cart = None
        logger.warning(f"Cart not found for user {user.username}")
    return cart


def add_to_cart(cart, product_variant):
    """

    """
    if not (isinstance(cart, CartModel) and isinstance(product_variant, ProductVariant)):
        logger.error(f"type error : please verify the cart and product type")
        return None, False
    if CartItem.objects.filter(cart=cart,product=product_variant).exists():
        logger.info('Product already present in the cart.')
        #cart_item = CartItem.objects.get(cart=cart, product=product)
        #quantity = cart_item.quantity + 1
        #return update_cart(cart, cart_item, quantity)
        return None

    cart_item = CartItem.objects.create(cart=cart, product=product_variant, quantity=1, unit_price=product_variant.price, total_price=product_variant.price)
    refresh_cart(cart)
    logger.info('Product added into the cart')
    return cart_item

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
        return "user params is not an instance of User", -1
    
    #aggregation = CartItem.objects.filter(cart__user=user).aggregate(count=Sum('quantity'), total=Sum(F('quantity')*F('unit_price'), output_field=FloatField()))
    #CartModel.objects.filter(id=cart.id).update(quantity=aggregation['count'], amount=aggregation['total'])
    items_count = 0
    cart = get_cart(user)
    if cart:
        items_count = cart.quantity
    
    return items_count