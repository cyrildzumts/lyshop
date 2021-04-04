from django.utils.translation import gettext_lazy as _
from lyshop import settings
VENDOR_GROUP = "Seller"
FEE_GROUP = "Fee"

SOLD_PRODUCT_SENT = 0
SOLD_PRODUCT_RECEIVED = 1
SOLD_PRODUCT_NOT_SENT = 2
SOLD_PRODUCT_RETURNED = 3
SOLD_PRODUCT_DELIVERED = 4

SOLD_PRODUCT_STATUS = (
    (SOLD_PRODUCT_SENT, 'PRODUCT SENT'),
    (SOLD_PRODUCT_RECEIVED, 'PRODUCT RECEIVED'),
    (SOLD_PRODUCT_NOT_SENT, 'PRODUCT NOT SENT'),
    (SOLD_PRODUCT_RETURNED, 'PRODUCT RETURNED'),
    (SOLD_PRODUCT_DELIVERED, 'PRODUCT DELIVERED'),
)

VENDOR_PAYMENT_DAY = settings.VENDOR_PAYMENT_DAY


DASHBOARD_GLOBALS_PREFIX = "vendors"


DASHBOARD_BRAND_CONTEXT = {
    'BRANDS_URL'               : f"{DASHBOARD_GLOBALS_PREFIX}:brands",
    'BRAND_URL'                : f"{DASHBOARD_GLOBALS_PREFIX}:brand-detail",
    'BRAND_UPDATE_URL'         : f"{DASHBOARD_GLOBALS_PREFIX}:brand-update",
    'BRAND_DELETE_URL'         : f"{DASHBOARD_GLOBALS_PREFIX}:brand-delete",
    'BRANDS_DELETE_URL'        : f"{DASHBOARD_GLOBALS_PREFIX}:brands-delete",
    'BRAND_CREATE_URL'         : f"{DASHBOARD_GLOBALS_PREFIX}:brand-create",
}

DASHBOARD_COUPON_CONTEXT = {
    'COUPONS_URL'               : f"{DASHBOARD_GLOBALS_PREFIX}:coupons",
    'COUPON_URL'                : f"{DASHBOARD_GLOBALS_PREFIX}:coupon-detail",
    'COUPON_UPDATE_URL'         : f"{DASHBOARD_GLOBALS_PREFIX}:coupon-update",
    'COUPON_DELETE_URL'         : f"{DASHBOARD_GLOBALS_PREFIX}:coupon-delete",
    'COUPONS_DELETE_URL'        : f"{DASHBOARD_GLOBALS_PREFIX}:coupons-delete",
    'COUPON_CREATE_URL'         : f"{DASHBOARD_GLOBALS_PREFIX}:coupon-create",
}

DASHBOARD_PRODUCT_CONTEXT = {
    'IMAGE_URL'                 : f"{DASHBOARD_GLOBALS_PREFIX}:product-image-detail",
    'IMAGE_CREATE_URL'          : f"{DASHBOARD_GLOBALS_PREFIX}:product-image-create",
    'IMAGE_DELETE_URL'          : f"{DASHBOARD_GLOBALS_PREFIX}:product-image-delete",
    'PRODUCTS_URL'              : f"{DASHBOARD_GLOBALS_PREFIX}:products",
    'PRODUCT_HOME_URL'          : f"{DASHBOARD_GLOBALS_PREFIX}:product-home",
    'PRODUCT_CREATE_URL'        : f"{DASHBOARD_GLOBALS_PREFIX}:product-create",
    'PRODUCT_DELETE_URL'        : f"{DASHBOARD_GLOBALS_PREFIX}:product-delete",
    'PRODUCTS_DELETE_URL'       : f"{DASHBOARD_GLOBALS_PREFIX}:products-delete",
    'PRODUCT_BULK_CHANGES_URL'  : f"{DASHBOARD_GLOBALS_PREFIX}:products-changes",
    'PRODUCT_URL'               : f"{DASHBOARD_GLOBALS_PREFIX}:product-detail",
    'PRODUCT_UPDATE_URL'        : f"{DASHBOARD_GLOBALS_PREFIX}:product-update",
    'VARIANT_URL'               : f"{DASHBOARD_GLOBALS_PREFIX}:product-variant-detail",
    'VARIANT_CREATE_URL'        : f"{DASHBOARD_GLOBALS_PREFIX}:product-variant-create",
    'VARIANT_UPDATE_URL'        : f"{DASHBOARD_GLOBALS_PREFIX}:product-variant-update",
    'VARIANT_DELETE_URL'        : f"{DASHBOARD_GLOBALS_PREFIX}:product-variant-delete",
}

DASHBOARD_SOLD_PRODUCT_CONTEXT = {
    'SOLD_PRODUCTS_URL'         : f"{DASHBOARD_GLOBALS_PREFIX}:sold-products",
    'SOLD_PRODUCT_URL'          : f"{DASHBOARD_GLOBALS_PREFIX}:sold-product-detail",
}

DASHBOARD_PRODUCT_TYPES_CONTEXT = {
    'PRODUCT_TYPES_URL'         : f"{DASHBOARD_GLOBALS_PREFIX}:product-types",
    'PRODUCT_TYPE_URL'          : f"{DASHBOARD_GLOBALS_PREFIX}:product-type-detail",
    'PRODUCT_TYPE_UPDATE_URL'   : f"{DASHBOARD_GLOBALS_PREFIX}:product-type-update",
    'PRODUCT_TYPE_DELETE_URL'   : f"{DASHBOARD_GLOBALS_PREFIX}:product-type-delete",
    'PRODUCT_TYPE_CREATE_URL'   : f"{DASHBOARD_GLOBALS_PREFIX}:product-type-create",
}

DASHBOARD_TYPES_ATTRIBUTE_CONTEXT = {
    'TYPE_ATTRIBUTES_URL'         : f"{DASHBOARD_GLOBALS_PREFIX}:product-type-attributes",
    'TYPE_ATTRIBUTE_URL'          : f"{DASHBOARD_GLOBALS_PREFIX}:product-type-attribute-detail",
    'TYPE_ATTRIBUTE_UPDATE_URL'   : f"{DASHBOARD_GLOBALS_PREFIX}:product-type-attribute-update",
    'TYPE_ATTRIBUTE_DELETE_URL'   : f"{DASHBOARD_GLOBALS_PREFIX}:product-type-attribute-delete",
    'TYPE_ATTRIBUTES_DELETE_URL'  : f"{DASHBOARD_GLOBALS_PREFIX}:product-type-attributes-delete",
    'TYPE_ATTRIBUTE_CREATE_URL'   : f"{DASHBOARD_GLOBALS_PREFIX}:product-type-attribute-create",
}

DASHBOARD_ATTRIBUTES_CONTEXT = {
    'ATTRIBUTE_BULK_CREATE_URL' : f"{DASHBOARD_GLOBALS_PREFIX}:bulk-attributes-create",
    'ATTRIBUTE_CREATE_URL'      : f"{DASHBOARD_GLOBALS_PREFIX}:attribute-create",
    'ATTRIBUTE_ADD_URL'         : f"{DASHBOARD_GLOBALS_PREFIX}:attribute-add",
    'ATTRIBUTES_URL'         : f"{DASHBOARD_GLOBALS_PREFIX}:attributes",
}

DASHBOARD_ORDERS_CONTEXT = {
    'ORDERS_URL'                : f"{DASHBOARD_GLOBALS_PREFIX}:orders",
    'ORDER_URL'                 : f"{DASHBOARD_GLOBALS_PREFIX}:order-detail",
    'ORDER_ITEM_URL'            : f"{DASHBOARD_GLOBALS_PREFIX}:order-item-detail",
    'ORDER_ITEM_UPDATE_URL'     : f"{DASHBOARD_GLOBALS_PREFIX}:order-item-update",
}

DASHBOARD_PAYMENTS_CONTEXT = {
    'PAYMENTS_URL'              : f"{DASHBOARD_GLOBALS_PREFIX}:payments",
    'PAYMENT_URL'               : f"{DASHBOARD_GLOBALS_PREFIX}:payment-detail",
}

