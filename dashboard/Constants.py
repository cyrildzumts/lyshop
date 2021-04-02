
APP_PREFIX = 'dashboard.'

SELLER_GROUP = "Seller"

MAX_RECENT = 5

DASHBOARD_GLOBALS_PREFIX = "dashboard"

DASHBOARD_PRODUCT_CONTEXT = {
    'IMAGE_URL'                 : f"{DASHBOARD_GLOBALS_PREFIX}:product-image-detail",
    'IMAGE_CREATE_URL'          : f"{DASHBOARD_GLOBALS_PREFIX}:product-image-create",
    'IMAGE_DELETE_URL'          : f"{DASHBOARD_GLOBALS_PREFIX}:product-image-delete",
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

DASHBOARD_PRODUCT_TYPES_CONTEXT = {
    'PRODUCT_TYPE_URL'          : f"{DASHBOARD_GLOBALS_PREFIX}:product-type-detail",
    'PRODUCT_TYPE_UPDATE_URL'   : f"{DASHBOARD_GLOBALS_PREFIX}:product-type-update",
    'PRODUCT_TYPE_DELETE_URL'   : f"{DASHBOARD_GLOBALS_PREFIX}:product-type-delete",
    'PRODUCT_TYPE_CREATE_URL'   : f"{DASHBOARD_GLOBALS_PREFIX}:product-type-create",
}


DASHBOARD_ATTRIBUTES_CONTEXT = {
    'ATTRIBUTE_BULK_CREATE_URL' : f"{DASHBOARD_GLOBALS_PREFIX}:bulk-attributes-create",
    'ATTRIBUTE_CREATE_URL' : f"{DASHBOARD_GLOBALS_PREFIX}:attribute-create",
    'ATTRIBUTE_ADD_URL' : f"{DASHBOARD_GLOBALS_PREFIX}:attribute-add",
}


DASHBOARD_VIEW_PERM = 'can_view_dashboard'
TOKEN_GENERATE_PERM = 'can_generate_token'

USER_VIEW_PERM = 'can_view_user'
USER_ADD_PERM = 'can_add_user'
USER_CHANGE_PERM = 'can_change_user'
USER_DELETE_PERM = 'can_delete_user'

ACCOUNT_VIEW_PERM = 'can_view_account'
ACCOUNT_ADD_PERM = 'can_add_account'
ACCOUNT_CHANGE_PERM = 'can_change_account'
ACCOUNT_DELETE_PERM = 'can_delete_account'

CASE_ISSUE_VIEW_PERM = 'can_view_claim'
CASE_ISSUE_ADD_PERM = 'can_add_claim'
CASE_ISSUE_CHANGE_PERM = 'can_change_claim'
CASE_ISSUE_DELETE_PERM = 'can_delete_claim'
CASE_ISSUE_CLOSE_PERM = 'can_close_claim'
GROUP_VIEW_PERM = 'can_view_group'
GROUP_ADD_PERM = 'can_add_group'
GROUP_CHANGE_PERM = 'can_change_group'
GROUP_DELETE_PERM = 'can_delete_group'

IDCARD_VIEW_PERM = 'can_view_idcard'
IDCARD_ADD_PERM = 'can_add_idcard'
IDCARD_CHANGE_PERM = 'can_change_idcard'
IDCARD_DELETE_PERM = 'can_delete_idcard'

PAYMENT_VIEW_PERM = 'can_view_payment'
PAYMENT_ADD_PERM = 'can_add_payment'
PAYMENT_CHANGE_PERM = 'can_change_payment'
PAYMENT_DELETE_PERM = 'can_delete_payment'

PRODUCT_VIEW_PERM = 'can_view_product'
PRODUCT_ADD_PERM = 'can_add_product'
PRODUCT_CHANGE_PERM = 'can_change_product'
PRODUCT_DELETE_PERM = 'can_delete_product'

POLICY_VIEW_PERM = 'can_view_policy'
POLICY_ADD_PERM = 'can_add_policy'
POLICY_CHANGE_PERM = 'can_change_policy'
POLICY_DELETE_PERM = 'can_delete_policy'

POLICY_GROUP_VIEW_PERM = 'can_view_policy_group'
POLICY_GROUP_ADD_PERM = 'can_add_policy_group'
POLICY_GROUP_CHANGE_PERM = 'can_change_policy_group'
POLICY_GROUP_DELETE_PERM = 'can_delete_policy_group'

POLICY_MEMBERSHIP_VIEW_PERM = 'can_view_policy_membership'
POLICY_MEMBERSHIP_ADD_PERM = 'can_add_policy_membership'
POLICY_MEMBERSHIP_CHANGE_PERM = 'can_change_policy_membership'
POLICY_MEMBERSHIP_DELETE_PERM = 'can_delete_policy_membership'

CATEGORY_VIEW_PERM = 'can_view_category'
CATEGORY_ADD_PERM = 'can_add_category'
CATEGORY_CHANGE_PERM = 'can_change_category'
CATEGORY_DELETE_PERM = 'can_delete_category'

BRAND_VIEW_PERM = 'can_view_brand'
BRAND_ADD_PERM = 'can_add_brand'
BRAND_CHANGE_PERM = 'can_change_brand'
BRAND_DELETE_PERM = 'can_delete_brand'

SERVICE_VIEW_PERM = 'can_view_service'
SERVICE_ADD_PERM = 'can_add_service'
SERVICE_CHANGE_PERM = 'can_change_service'
SERVICE_DELETE_PERM = 'can_delete_service'

SHIPMENT_VIEW_PERM = 'can_view_shipment'
SHIPMENT_ADD_PERM = 'can_add_shipment'
SHIPMENT_CHANGE_PERM = 'can_change_shipment'
SHIPMENT_DELETE_PERM = 'can_delete_shipment'

ORDER_VIEW_PERM = 'can_view_order'
ORDER_ADD_PERM = 'can_add_order'
ORDER_CHANGE_PERM = 'can_change_order'
ORDER_DELETE_PERM = 'can_delete_order'

COUPON_VIEW_PERM = 'can_view_coupon'
COUPON_ADD_PERM = 'can_add_coupon'
COUPON_CHANGE_PERM = 'can_change_coupon'
COUPON_DELETE_PERM = 'can_delete_coupon'
