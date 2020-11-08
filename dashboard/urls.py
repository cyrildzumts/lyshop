from django.conf.urls import url, include
from django.urls import path, reverse_lazy
# from demosite import settings
from dashboard import views

app_name = 'dashboard'
urlpatterns = [
    path('', views.dashboard, name='home'),

    
    path('brands/', views.brands, name='brands'),
    path('brands/create/', views.brand_create, name='brand-create'),
    path('brands/update/<uuid:brand_uuid>/', views.brand_update, name='brand-update'),
    path('brands/delete/<uuid:brand_uuid>/', views.brand_delete, name='brand-delete'),
    path('brands/delete/', views.brands_delete, name='brands-delete'),
    #path('brands/remove-all/', views.brand_remove_all, name='brand-remove-all'),
    path('brands/detail/<uuid:brand_uuid>/', views.brand_detail, name='brand-detail'),
    path('brands/products/<uuid:brand_uuid>/<uuid:product_uuid>/', views.brand_product_detail, name='brand-product'),

    path('categories/', views.categories, name='categories'),
    path('categories/detail/<uuid:category_uuid>/', views.category_detail, name='category-detail'),
    path('categories/delete/<uuid:category_uuid>/', views.category_delete, name='category-delete'),
    path('categories/delete/', views.categories_delete, name='categories-delete'),
    path('categories/update/<uuid:category_uuid>/', views.category_update, name='category-update'),
    path('categories/create/', views.category_create, name='category-create'),

    path('coupon-create/',views.coupon_create, name='coupon-create'),
    path('coupon-detail/<uuid:coupon_uuid>/',views.coupon_detail, name='coupon-detail'),
    path('coupon-delete/<uuid:coupon_uuid>/',views.coupon_delete, name='coupon-delete'),
    path('coupon-update/<uuid:coupon_uuid>/',views.coupon_update, name='coupon-update'),
    path('coupons/',views.coupons, name='coupons'),
    path('coupons/delete/',views.coupons_delete, name='coupons-delete'),

    #path('cases/', views.cases, name='cases'),
    #path('cases/detail/<issue_uuid>/', views.case_details, name='case-detail'),
    #path('cases/close/<issue_uuid>/', views.case_close, name='case-close'),
    path('create-account/',views.create_account, name='create-account'),
    path('generate-token/', views.generate_token, name='generate-token'),
    path('group-create/',views.group_create, name='group-create'),
    path('group-detail/<int:pk>/',views.group_detail, name='group-detail'),
    path('group-delete/<int:pk>/',views.group_delete, name='group-delete'),
    path('group-update/<int:pk>/',views.group_update, name='group-update'),
    path('groups/',views.groups, name='groups'),
    path('groups/delete/',views.groups_delete, name='groups-delete'),

    path('highlights/', views.highlights, name='highlights'),
    path('highlights/detail/<uuid:highlight_uuid>/', views.highlight_detail, name='highlight-detail'),
    path('highlights/update/<uuid:highlight_uuid>/', views.highlight_update, name='highlight-update'),
    path('highlights/delete/<uuid:highlight_uuid>/', views.highlight_delete, name='highlight-delete'),
    path('highlights/delete/', views.highlights_delete, name='highlights-delete'),
    path('highlights/create/', views.highlight_create, name='highlight-create'),
    path('highlights/add-products/<uuid:highlight_uuid>/', views.highlight_add_products, name='highlight-add-products'),

    path('orders/', views.orders, name='orders'),
    path('orders/detail/<uuid:order_uuid>/', views.order_detail, name='order-detail'),
    path('orders/order-item/<uuid:order_uuid>/<uuid:item_uuid>/', views.order_item, name='order-item'),
    path('orders/order-item/update/<uuid:order_uuid>/<uuid:item_uuid>/', views.order_item_update, name='order-item-update'),
    path('orders/cancel/<uuid:order_uuid>/', views.order_cancel, name='order-cancel'),
    path('orders/add-order-for-shipment/<uuid:order_uuid>/', views.add_order_for_shipment, name='add-order-for-shipment'),
    path('orders/update/<uuid:order_uuid>/', views.order_update, name='order-update'),
    path('orders/history/<uuid:order_uuid>/', views.order_history, name='order-history'),
    path('orders/history/detail/<uuid:history_uuid>/', views.order_history_detail, name='order-history-detail'),

    path('products/', views.products, name='products'),
    path('products/detail/<uuid:product_uuid>/', views.product_detail, name='product-detail'),
    path('products/update/<uuid:product_uuid>/', views.product_update, name='product-update'),
    path('products/delete/<uuid:product_uuid>/', views.product_delete, name='product-delete'),
    path('products/delete/', views.products_delete, name='products-delete'),
    path('products/create/', views.product_create, name='product-create'),

    path('product-types/', views.product_types, name='product-types'),
    path('product-types/detail/<uuid:type_uuid>/', views.product_type_detail, name='product-type-detail'),
    path('product-types/update/<uuid:type_uuid>/', views.product_type_update, name='product-type-update'),
    path('product-types/delete/<uuid:type_uuid>/', views.product_type_delete, name='product-type-delete'),
    path('product-types/delete/', views.product_types_delete, name='product-types-delete'),
    path('product-types/create/', views.product_type_create, name='product-type-create'),

    path('product-type-attributes/', views.product_type_attributes, name='product-type-attributes'),
    path('product-type-attributes/detail/<uuid:type_attribute_uuid>/', views.product_type_attribute_detail, name='product-type-attribute-detail'),
    path('product-type-attributes/update/<uuid:type_attribute_uuid>/', views.product_type_attribute_update, name='product-type-attribute-update'),
    path('product-type-attributes/delete/<uuid:type_attribute_uuid>/', views.product_type_attribute_delete, name='product-type-attribute-delete'),
    path('product-type-attributes/delete/', views.product_type_attributes_delete, name='product-type-attributes-delete'),
    path('product-type-attributes/create/', views.product_type_attribute_create, name='product-type-attribute-create'),

    path('products/product-images/<uuid:product_uuid>/', views.product_images, name='product-images'),
    path('products/product-image/detail/<uuid:image_uuid>/', views.product_image_detail, name='product-image-detail'),
    path('products/product-image/update/<uuid:image_uuid>/', views.product_image_update, name='product-image-update'),
    path('products/product-image/delete/<uuid:image_uuid>/', views.product_image_delete, name='product-image-delete'),
    path('products/product-image/create/<uuid:product_uuid>', views.product_image_create, name='product-image-create'),

    path('products/product-variant/detail/<uuid:variant_uuid>/', views.product_variant_detail, name='product-variant-detail'),
    path('products/product-variant/update/<uuid:variant_uuid>/', views.product_variant_update, name='product-variant-update'),
    path('products/product-variant/delete/<uuid:variant_uuid>/', views.product_variant_delete, name='product-variant-delete'),
    path('products/product-variant/create/<uuid:product_uuid>/', views.product_variant_create, name='product-variant-create'),

    path('products/attributes/', views.attributes, name='attributes'),
    path('products/attributes/detail/<uuid:attribute_uuid>/', views.attribute_detail, name='attribute-detail'),
    path('products/attributes/update/<uuid:attribute_uuid>/', views.attribute_update, name='attribute-update'),
    path('products/attributes/delete/', views.delete_attributes, name='attributes-delete'),
    path('products/attributes/delete/<uuid:attribute_uuid>/', views.attribute_delete, name='attribute-delete'),
    path('products/attributes/create/<uuid:variant_uuid>/', views.attribute_create, name='attribute-create'),
    path('products/attributes/create/', views.attributes_create, name='attributes-create'),
    path('products/attributes/add/<uuid:variant_uuid>/', views.add_attributes, name='attribute-add'),
    path('products/attributes/remove/<uuid:variant_uuid>/', views.remove_attributes, name='attribute-remove'),
    path('products/attributes/update-default-primary/', views.update_primary_attributes, name='attribute-primary-update'),


    path('payment-requests/', views.payment_requests, name='payment-requests'),
    path('payment-requests/detail/<uuid:request_uuid>/', views.payment_request_details, name='payment-request-detail'),
    path('policies/', views.policies, name='policies'),
    path('policies/detail/<uuid:policy_uuid>/', views.policy_details, name='policy-detail'),
    path('policies/remove/<uuid:policy_uuid>/', views.policy_remove, name='policy-remove'),
    path('policies/remove-all/', views.policy_remove_all, name='policy-remove-all'),
    path('policies/update/<uuid:policy_uuid>/', views.policy_update, name='policy-update'),
    path('policies/create/', views.policy_create, name='policy-create'),
    path('policies/delete/', views.policies_delete, name='policies-delete'),

    path('policy-groups/', views.policy_groups, name='policy-groups'),
    path('policy-groups/delete', views.policy_groups_delete, name='policy-groups-delete'),
    path('policy-groups/detail/<uuid:group_uuid>/', views.policy_group_details, name='policy-group-detail'),
    path('policy-groups/update-members/<uuid:group_uuid>/', views.policy_group_update_members, name='policy-group-update-members'),
    path('policy-groups/remove/<uuid:group_uuid>/', views.policy_group_remove, name='policy-group-remove'),
    #path('policy-groups/remove-all/', views.policy_remove_all, name='policy-group-remove-all'),
    path('policy-groups/update/<uuid:group_uuid>/', views.policy_group_update, name='policy-group-update'),
    path('policy-groups/create/', views.policy_group_create, name='policy-group-create'),
    path('reports/', views.reports, name='reports'),

    path('sold-products/', views.sold_product_list, name='sold-products'),
    path('sold-products/details/<uuid:product_uuid>/', views.sold_product_detail, name='sold-product-detail'),
    path('sold-products/delete/<uuid:product_uuid>/', views.sold_product_delete, name='sold-product-delete'),
    path('sold-products/delete/', views.sold_products_delete, name='sold-products-delete'),

    path('tokens/', views.tokens, name='tokens'),
    path('users/', views.users, name='users'),
    path('users/create-user/', views.create_account, name='create-user'),
    path('users/detail/<int:pk>', views.user_details, name='user-detail'),
    path('users/create-balance/<int:pk>', views.create_vendor_balance, name='create-vendor-balance'),
    path('users/reset/<int:pk>', views.reset_vendor, name='reset-vendor'),
    path('users/update-vendor-sold-product/<int:pk>', views.update_vendor_products, name='update-vendors-products'),
    
    
]