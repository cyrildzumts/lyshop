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

    path('products/', views.products, name='products'),
    path('products/detail/<uuid:product_uuid>/', views.product_detail, name='product-detail'),
    path('products/update/<uuid:product_uuid>/', views.product_update, name='product-update'),
    path('products/delete/<uuid:product_uuid>/', views.product_delete, name='product-delete'),
    path('products/create/', views.create_product, name='product-create'),

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
    path('products/attributes/add/<uuid:variant_uuid>/', views.add_attributes, name='attribute-add'),
    path('products/attributes/remove/<uuid:variant_uuid>/', views.remove_attributes, name='attribute-remove'),

    #path('payment-requests/', views.payment_requests, name='payment-requests'),
    #path('payment-requests/detail/<uuid:request_uuid>/', views.payment_request_details, name='payment-request-detail'),
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
    path('tokens/', views.tokens, name='tokens'),
    path('users/', views.users, name='users'),
    path('users/create-user/', views.create_account, name='create-user'),
    path('users/detail/<int:pk>', views.user_details, name='user-detail'),
    
    
]