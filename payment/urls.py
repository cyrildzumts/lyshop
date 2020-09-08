from django.conf.urls import url, include
from django.urls import path, reverse_lazy
# from demosite import settings
from payment import views

app_name = 'payment'
urlpatterns = [
    path('', views.payment_home, name='payment-home'),
    path('payments/', views.payments, name='payments'),
    path('payments/detail/<uuid:payment_uuid>/', views.payment_details, name='payment-detail'),
    path('pay-vendor/<int:vendor_pk>/', views.pay_vendor, name='pay-vendor'),
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
    #path('reports/', views.reports, name='reports'),


]