from django.db.models import F,Q,Count, Sum, FloatField, When, Case
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from cart.models import CartItem, CartModel, Coupon
from catalog.models import ProductVariant, Product
import logging
import datetime

logger = logging.getLogger(__name__)



def refresh_cart(cart):
    cart_exist = False
    if cart:
        cartitems = CartItem.objects.filter(cart=cart)
        cart_exist = cartitems.exists()
        if  cart_exist:
            annotation = cartitems.annotate(
                active_price=Case(
                    When(product__promotion_price__isnull=False, then='product__promotion_price'),
                    When(product__product__promotion_price__isnull=False, then='product__product__promotion_price'),
                    default='unit_price',
                    output_field=FloatField()
                )
            )
            aggregation = annotation.values_list('quantity', 'active_price').aggregate(count=Sum('quantity'), total=Sum(F('quantity')*F('active_price'), output_field=FloatField()))
            CartModel.objects.filter(id=cart.id).update(quantity=aggregation['count'], amount=aggregation['total'])
            cart.refresh_from_db()
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
        CartModel.objects.filter(pk=cart.pk).update(coupon=None, amount=0, solded_price=0, quantity=0)
        logger.debug(f"Cart for user {user.username} has been clearded. {num_of_deleted_objects} Cartitems deleted")
        cart.refresh_from_db()
    return cart


def get_cart_solded_price(amount=0.0, percent=0):
    solded_price = None
    if amount and percent:
        solded_price = float(amount) *((100 - percent) / 100.0)
    return solded_price


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
        updated_rows, cart_item = update_cart(cart, cart_item, cart_item.quantity + 1)
        if updated_rows > 0:
            return cart_item, cart
        else:
            return None, cart
    total = product_variant.active_price
    cart_item = CartItem.objects.create(cart=cart, product=product_variant, quantity=1, unit_price=product_variant.price, total_price=total)
    solded_price = 0
    if cart.coupon:
        solded_price = get_cart_solded_price(cart.amount + cart_item.item_total_price, cart.coupon.reduction)
    CartModel.objects.filter(pk=cart.pk).update(quantity=F('quantity') + 1, amount=F('amount') + cart_item.item_total_price, solded_price=solded_price)
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
        return 0, cart_item

    if quantity <= cart_item.product.quantity:
        item_old_quantity = cart_item.quantity
        item_old_total_price = cart_item.item_total_price
        updated_rows = CartItem.objects.filter(id=cart_item.id, is_active=True).update(quantity=quantity, total_price=F('unit_price') * quantity)
        cart_item.refresh_from_db()
        cart_quantity = cart.quantity - item_old_quantity + quantity
        cart_amount = cart.amount - item_old_total_price + cart_item.item_total_price
        cart_solded_price = 0
        if cart.coupon:
            cart_solded_price = get_cart_solded_price(float(cart_amount), cart.coupon.reduction)
        CartModel.objects.filter(pk=cart.pk).update(quantity=cart_quantity, amount=cart_amount, solded_price=cart_solded_price)
        logger.info(f'update_cart : {updated_rows} row(s) in Cart Item updated quantity field to {quantity}')
        return updated_rows, cart_item

    else:
        if cart_item.product.quantity == 0 and cart_item.product.is_active:
            CartItem.objects.filter(id=cart_item.id).update(is_active=False)
        logger.warning('update_cart : The required quantity is not available')
        return -1, cart_item

    return None, cart_item


def remove_from_cart(cart, cart_item=None):
    logger.info(f"Removing Cart Item \"{cart_item}\" from Cart \"{cart}\"")
    item_quantity = cart_item.quantity
    item_total_price = cart_item.item_total_price
    old_card_quantity = cart.quantity
    deleted_count, delete_items = CartItem.objects.filter(id=cart_item.id, cart=cart).delete()
    if deleted_count:
        logger.info(f"Removed Cart Item \"{cart_item}\" from Cart \"{cart}\"")
        if cart_item.quantity == cart.quantity:
            CartModel.objects.filter(pk=cart.pk).update(quantity=0, amount=0, solded_price=0)
            logger.info(f"Cleared Cart \"{cart}\"")
        else:
            solded_price = cart.amount
            if cart.coupon:
                solded_price = float(cart.amount) - cart.get_reduction()
            CartModel.objects.filter(pk=cart.pk).update(quantity=F('quantity') - cart_item.quantity, amount=F('amount')-cart_item.item_total_price, solded_price=solded_price)
            logger.info(f"Updated Cart \"{cart}\"")
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
        cartitems_queryset = CartItem.objects.select_related('product').prefetch_related('product__attributes').filter(cart=cart)
    return cartitems_queryset

def is_valid_coupon(coupon):
    if not isinstance(coupon, str) :
        return False
    coupon_exists = Coupon.objects.filter(name=coupon, is_active=True, expire_at__gte=datetime.datetime.now()).exists()
    logger.info(f"Coupon \"{coupon}\" is valid :  \"{coupon_exists}\"")
    
    return coupon_exists
    

def apply_coupon(cart, coupon):
    if not isinstance(cart, CartModel) or not isinstance(coupon, str) :
        return False
    try:
        coupon_model = Coupon.objects.get(name=coupon, is_active=True, expire_at__gte=timezone.now())
        solded_price = coupon_model.get_solded_price(cart.amount)
        CartModel.objects.filter(pk=cart.pk).update(coupon=coupon_model, solded_price=solded_price)
        logger.info(f"Coupon \"{coupon}\" applied to Cart for user \"{cart.user.username}\"")
    except ObjectDoesNotExist as e:
        logger.warn(f"No coupon found with the name \"{coupon}\"")
        return False
    return True

def remove_coupon(cart):
    if not isinstance(cart, CartModel):
        return False
    if not cart.coupon:
        return False
    
    CartModel.objects.filter(pk=cart.pk).update(coupon=None, solded_price=0)


def coupons_cleanup():
    coupon_set = Coupon.objects.filter(is_active=True, expire_at__lt=timezone.now())
    cart_set = CartModel.objects.filter(coupon__in=coupon_set)
    cart_count = cart_set.count()
    coupon_count = coupon_set.count()
    logger.info(f"coupons_cleanup : Found {coupon_count} expired coupon.")
    logger.info(f"coupons_cleanup : Found {cart_count} Carts using expired coupons.")
    coupon_set.update(is_active=False)
    cart_set.update(coupon=None, solded_price=0)
    logger.info(f"coupons_cleanup : Finished cleaning expired coupons.")
