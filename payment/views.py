from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied, SuspiciousOperation, ObjectDoesNotExist

from django.contrib.auth.models import User, Group, Permission
from django.http import Http404
from django.http import HttpResponseRedirect
from django.http import HttpResponseBadRequest
from django.http import HttpResponse
from django.urls import reverse, resolve
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseForbidden
from django.contrib import messages
from payment.models import Payment, PaymentHistory, PaymentPolicy, PaymentPolicyGroup
from payment.forms import PaymentPolicyForm, PaymentPolicyGroupForm, PaymentPolicyGroupUpdateForm, PaymentPolicyGroupUpdateMembersForm
from dashboard.permissions import PermissionManager, get_view_permissions
from payment import payment_service
from lyshop import settings, utils
import json
import logging

logger = logging.getLogger(__name__)
# Create your views here.


@login_required
def payment_home(request):
    username = request.user.username
    if not PermissionManager.user_can_view_payment(request.user):
        logger.warning("Payment Page : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    template_name = "payment/payment_home.html"
    page_title = _("Payment-Home")

    
    
    recent_payments = Payment.objects.select_related().order_by('-created_at')[:5]

    context = {
        'page_title' : page_title,
        'recent_payments' : recent_payments,
    }
    context.update(get_view_permissions(request.user))
    return render(request, template_name, context)


@login_required
def payments(request):
    username = request.user.username

    can_view_payment = PermissionManager.user_can_view_payment(request.user)
    if not can_view_payment:
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    context = {}
    queryset = Payment.objects.all()
    template_name = "payment/payment_list.html"
    page_title = "Payments - " + settings.SITE_NAME
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, utils.PAGINATED_BY)
    try:
        list_set = paginator.page(page)
    except PageNotAnInteger:
        list_set = paginator.page(1)
    except EmptyPage:
        list_set = None
    context['page_title'] = page_title
    context['payment_list'] = list_set
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)


@login_required
def payment_details(request, payment_uuid=None):
    username = request.user.username

    can_view_payment = PermissionManager.user_can_view_policy(request.user)
    if not can_view_payment:
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    context = {}
    payment = get_object_or_404(Payment, payment_uuid=payment_uuid)
    template_name = "payment/payment_detail.html"
    page_title = "Payment Details - " + settings.SITE_NAME
    context['page_title'] = page_title
    context['payment'] = payment
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)


@login_required
def pay_vendor(requets, vendor_pk):
    username = request.user.username

    can_view_payment = PermissionManager.user_can_view_policy(request.user)
    if not can_view_payment:
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    vendor = get_object_or_404(User, pk=vendor_pk)
    payment = payment_service.process_vendor_payment(vendor)
    if payment:
        messages.success(request, f"Payment for vendor {vendor.username} processed")
    else:
        messages.warning(request, f"Payment for vendor {vendor.username} not processed")
    
    return redirect('dashboard:users')

@login_required
def policies(request):
    username = request.user.username
    can_access_dashboard = PermissionManager.user_can_access_dashboard(request.user)
    if not can_access_dashboard:
        logger.warning("Payment : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    can_view_policy = PermissionManager.user_can_view_policy(request.user)
    if not can_view_policy:
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    context = {}
    queryset = PaymentPolicy.objects.all()
    template_name = "payment/policy_list.html"
    page_title = "Policies - " + settings.SITE_NAME
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, utils.PAGINATED_BY)
    try:
        list_set = paginator.page(page)
    except PageNotAnInteger:
        list_set = paginator.page(1)
    except EmptyPage:
        list_set = None
    context['page_title'] = page_title
    context['policies'] = list_set
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)


@login_required
def policy_update(request, policy_uuid=None):
    username = request.user.username
    can_access_dashboard = PermissionManager.user_can_access_dashboard(request.user)
    if not can_access_dashboard:
        logger.warning("Payment : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    can_change_policy = PermissionManager.user_can_change_policy(request.user)
    if not can_change_policy:
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    page_title = _("Edit Policy")+ ' | ' + settings.SITE_NAME
    instance = get_object_or_404(PaymentPolicy, policy_uuid=policy_uuid)
    template_name = "payment/policy_update.html"
    if request.method =="POST":
        form = PaymentPolicyForm(request.POST, instance=instance)
        if form.is_valid():
            logger.info("PaymentPolicyForm for instance %s is valid", form.cleaned_data['commission'])
            form.save()
            return redirect('payment:policies')
        else:
            logger.info("[failed] Edit PaymentPolicyForm commission : %s", request.POST.copy()['commission'])
            logger.info("Edit PaymentPolicyForm is not valid. Errors : %s", form.errors)
    
    form = PaymentPolicyForm(instance=instance)
    context = {
            'page_title':page_title,
            'template_name':template_name,
            'policy' : instance,
            'form': form,
            'can_change_policy' : can_change_policy
        }
    context.update(get_view_permissions(request.user))
    return render(request, template_name,context )



@login_required
def policy_remove(request, policy_uuid=None):
    # TODO Check if the user requesting the deletion has the permission
    username = request.user.username
    can_access_dashboard = PermissionManager.user_can_access_dashboard(request.user)
    if not can_access_dashboard:
        logger.warning("Payment : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    can_delete_policy = PermissionManager.user_can_delete_policy(request.user)
    if not can_delete_policy:
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    deleted_count, extras = PaymentPolicy.objects.filter(policy_uuid=policy_uuid).delete()
    if deleted_count > 0 :
        messages.add_message(request, messages.SUCCESS, 'PaymentPolicy has been deleted')
        logger.debug("PaymentPolicy deleted by User {}", request.user.username)
    
    else:
        messages.add_message(request, messages.ERROR, 'PaymentPolicy could not be deleted')
        logger.error("Policy Delete failed. Action requested by User {}",request.user.username)
        
    return redirect('payment:policies')


@login_required
def policies_delete(request):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Payment : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_delete_policy(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if request.method != "POST":
        raise SuspiciousOperation('Bad request. Expected POST request but received a GET')
    
    postdata = utils.get_postdata(request)
    id_list = postdata.getlist('policies')

    if len(id_list):
        instance_list = list(map(int, id_list))
        PaymentPolicy.objects.filter(id__in=instance_list).delete()
        messages.success(request, f"Policies \"{instance_list}\" deleted")
        logger.info(f"Policies \"{instance_list}\" deleted by user {username}")
        
    else:
        messages.error(request, f"Policies could not be deleted")
        logger.error(f"ID list invalid. Error : {id_list}")
    return redirect('payment:policies')


@login_required
def policy_remove_all(request):
    # TODO Check if the user requesting the deletion has the permission
    username = request.user.username
    can_access_dashboard = PermissionManager.user_can_access_dashboard(request.user)
    if not can_access_dashboard:
        logger.warning("Payment : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    can_delete_policy = PermissionManager.user_can_delete_policy(request.user)
    if not can_delete_policy:
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    deleted_count, extras = PaymentPolicy.objects.delete()
    if deleted_count > 0 :
        messages.add_message(request, messages.SUCCESS, 'All Policies has been deleted')
        logger.debug("All Policies deleted by User {}", request.user.username)
    
    else:
        messages.add_message(request, messages.ERROR, 'All Policies could not be deleted')
        logger.error("All Policies Delete failed. Action requested by User {}",request.user.username)
        
    return redirect('payment:payment-home')

@login_required
def policy_create(request):
    username = request.user.username
    can_access_dashboard = PermissionManager.user_can_access_dashboard(request.user)
    if not can_access_dashboard:
        logger.warning("Payment : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    can_add_policy = PermissionManager.user_can_add_policy(request.user)
    if not can_add_policy:
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    page_title = _("Create Policy")+ ' | ' + settings.SITE_NAME
    template_name = "payment/policy_create.html"
    form = None
    if request.method =="POST":
        form = PaymentPolicyForm(request.POST)
        if form.is_valid():
            logger.info("PaymentPolicyForm for instance %s is valid", form.cleaned_data['commission'])
            form.save()
            return redirect('payment:policies')
        else:
            form = PaymentPolicyForm()
            logger.info("Edit PaymentPolicyForm is not valid. Errors : %s", form.errors)
    elif request.method == "GET":
        form = PaymentPolicyForm()

    context = {
            'page_title':page_title,
            'template_name':template_name,
            'form': form,
            'can_add_policy' : can_add_policy
        }
    
    context.update(get_view_permissions(request.user))
    return render(request, template_name,context )


@login_required
def policy_details(request, policy_uuid=None):
    username = request.user.username
    can_access_dashboard = PermissionManager.user_can_access_dashboard(request.user)
    if not can_access_dashboard:
        logger.warning("Payment : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    can_view_policy = PermissionManager.user_can_view_policy(request.user)
    if not can_view_policy:
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    context = {}
    policy = get_object_or_404(PaymentPolicy, policy_uuid=policy_uuid)
    template_name = "payment/policy_detail.html"
    page_title = "Policy Details - " + settings.SITE_NAME
    context['page_title'] = page_title
    context['policy'] = policy
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)


@login_required
def policy_groups(request):
    username = request.user.username
    can_access_dashboard = PermissionManager.user_can_access_dashboard(request.user)
    if not can_access_dashboard:
        logger.warning("Payment : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    can_view_policy = PermissionManager.user_can_view_policy(request.user)
    can_add_policy = PermissionManager.user_can_add_policy(request.user)
    if not can_view_policy:
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    context = {}
    queryset = PaymentPolicyGroup.objects.all()
    template_name = "payment/policy_group_list.html"
    page_title = "Policy Group - " + settings.SITE_NAME
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, utils.PAGINATED_BY)
    try:
        list_set = paginator.page(page)
    except PageNotAnInteger:
        list_set = paginator.page(1)
    except EmptyPage:
        list_set = None
    context['page_title'] = page_title
    context['groups'] = list_set
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)


@login_required
def policy_group_create(request):
    username = request.user.username
    can_access_dashboard = PermissionManager.user_can_access_dashboard(request.user)
    if not can_access_dashboard:
        logger.warning("Payment : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    can_add_policy = PermissionManager.user_can_add_policy(request.user)
    if not can_add_policy:
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    page_title = _("Create Policy Group") + ' | ' + settings.SITE_NAME
    template_name = "payment/policy_group_create.html"
    form = None
    if request.method =="POST":
        form = PaymentPolicyGroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('payment:policy-groups')
        else:
            logger.info("Edit PaymentPolicyGroupForm is not valid. Errors : %s", form.errors)
    elif request.method == "GET":
        form = PaymentPolicyGroupForm()

    context = {
            'page_title':page_title,
            'template_name':template_name,
            'form': form,
            'policies' : PaymentPolicy.objects.all(),
            'can_add_policy' : can_add_policy
        }
    context.update(get_view_permissions(request.user))
    
    return render(request, template_name,context )

@login_required
def policy_group_update(request, group_uuid=None):
    username = request.user.username
    can_access_dashboard = PermissionManager.user_can_access_dashboard(request.user)
    if not can_access_dashboard:
        logger.warning("payment : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    can_change_policy = PermissionManager.user_can_change_policy(request.user)
    if not can_change_policy:
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    page_title = _("Edit Payment Policy Group")+ ' | ' + settings.SITE_NAME
    instance = get_object_or_404(PaymentPolicyGroup, policy_group_uuid=group_uuid)
    template_name = "payment/policy_group_update.html"
    if request.method =="POST":
        form = PaymentPolicyGroupUpdateForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('payment:policy-groups')
        else:
            logger.info("Edit PaymentPolicyGroupUpdateForm is not valid. Errors : %s", form.errors)
    
    form = PaymentPolicyGroupForm(instance=instance)
    context = {
            'page_title':page_title,
            'template_name':template_name,
            'group' : instance,
            'form': form,
            'policies' : PaymentPolicy.objects.all(),
            'can_change_policy' : can_change_policy
        }
    context.update(get_view_permissions(request.user))
    return render(request, template_name,context )


@login_required
def policy_group_update_members(request, group_uuid=None):
    username = request.user.username
    can_access_dashboard = PermissionManager.user_can_access_dashboard(request.user)
    if not can_access_dashboard:
        logger.warning("Payment : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    can_change_policy = PermissionManager.user_can_change_policy(request.user)
    if not can_change_policy:
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    page_title = _("Edit Policy Group")+ ' | ' + settings.SITE_NAME
    instance = get_object_or_404(PaymentPolicyGroup, policy_group_uuid=group_uuid)
    template_name = "payment/policy_group_update.html"
    if request.method =="POST":
        form = PaymentPolicyGroupUpdateForm(request.POST, instance=instance)
        if form.is_valid():
            # user can not be members on more han one group at the same time.
            #old_members = instance.members.all()
            new_members = form.cleaned_data.get('members')
            logger.info('new members : %s', new_members)
            for u in new_members:
                u.paymentpolicygroup_set.clear()
            
            instance.members.clear()
            form.save()
            messages.success(request, "Policy Group {} updated".format(instance.name))
            return redirect('payment:policy-groups')
        else:
            messages.error(request, "Policy Group {} could not updated. Invalid form".format(instance.name))
            logger.info("Edit PolicyGroupUpdateForm is not valid. Errors : %s", form.errors)
            return redirect(instance.get_absolute_url())
    messages.error(request, "Invalid request")
    return redirect(instance.get_absolute_url())


@login_required
def policy_group_details(request, group_uuid=None):
    username = request.user.username
    can_access_dashboard = PermissionManager.user_can_access_dashboard(request.user)
    if not can_access_dashboard:
        logger.warning("Payment : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    can_view_policy = PermissionManager.user_can_view_policy(request.user)
    if not can_view_policy:
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    context = {}
    group = get_object_or_404(PaymentPolicyGroup, policy_group_uuid=group_uuid)
    template_name = "payment/policy_group_detail.html"
    page_title = "Policy Group Details - " + settings.SITE_NAME
    context['page_title'] = page_title
    context['group'] = group
    context['members'] = group.members.all()
    context['users'] = User.objects.filter(is_active=True, is_superuser=False)
    context.update(get_view_permissions(request.user))
    return render(request,template_name, context)

@login_required
def policy_group_remove(request, group_uuid=None):
    # TODO Check if the user requesting the deletion has the permission
    username = request.user.username
    can_access_dashboard = PermissionManager.user_can_access_dashboard(request.user)
    if not can_access_dashboard:
        logger.warning("Dashboard : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    can_delete_policy = PermissionManager.user_can_delete_policy(request.user)
    if not can_delete_policy:
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    deleted_count, extras = PaymentPolicyGroup.objects.filter(policy_group_uuid=group_uuid).delete()
    if deleted_count > 0 :
        messages.success(request, 'PolicyGroup has been deleted')
        logger.info("Policy Group deleted by User {}", request.user.username)
    
    else:
        messages.error(request, 'Policy Group could not be deleted')
        logger.error("Policy Group Delete failed. Action requested by User {}",request.user.username)
        
    return redirect('payment:policy-groups')


@login_required
def policy_groups_delete(request):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Payment : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_delete_policy(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if request.method != "POST":
        raise SuspiciousOperation('Bad request. Expected POST request but received a GET')
    
    postdata = utils.get_postdata(request)
    id_list = postdata.getlist('policies-groups')

    if len(id_list):
        instance_list = list(map(int, id_list))
        PaymentPolicyGroup.objects.filter(id__in=instance_list).delete()
        messages.success(request, f"Policies Groups \"{instance_list}\" deleted")
        logger.info(f"Policies Groups \"{instance_list}\" deleted by user {username}")
        
    else:
        messages.error(request, f"Policies Groups could not be deleted")
        logger.error(f"ID list invalid. Error : {id_list}")
    return redirect('payment:policy-groups')



@login_required
def payment_dates(request):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Payment : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_delete_policy(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied


@login_required
def payment_date_detail(request, date_uuid):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Payment : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_delete_policy(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied


@login_required
def payment_date_update(request, date_uuid):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Payment : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_delete_policy(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied


@login_required
def payment_date_delete(request, date_uuid):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Payment : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_delete_policy(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied


@login_required
def payment_date_groups(request):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Payment : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_delete_policy(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied



@login_required
def payment_date_groups_detail(request, group_uuid):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Payment : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_delete_policy(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied



@login_required
def payment_date_groups_update(request, group_uuid):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Payment : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_delete_policy(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied


@login_required
def payment_date_groups_delete(request, group_uuid):
    username = request.user.username
    if not PermissionManager.user_can_access_dashboard(request.user):
        logger.warning("Payment : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    if not PermissionManager.user_can_delete_policy(request.user):
        logger.warning("PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied