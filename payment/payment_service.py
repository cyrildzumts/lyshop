from django.db.models import F,Q,Count, Sum, FloatField
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from payment.models import Payment, PaymentHistory, PaymentPolicy, PaymentPolicyGroup
from vendors import vendors_service
from vendors.models import Balance, BalanceHistory
from lyshop import settings
import requests
import json
import logging
import uuid


logger = logging.getLogger(__name__)


def get_commission(amount, commision):
        fee = 0
        vendor_amount = 0
        succeed = False
        if isinstance(amount, numbers.Number) and isinstance(commision, numbers.Number):
            fee = round(amount * commision, 2)
            vendor_amount = amount - fee
            succeed = True
        else:
            logger.error("get_commison called with wrong parameter type")
        #logger.info(f"Commission : {commision} - Fee : {fee} - Amount : {amount} - Vendor Amount : {vendor_amount}")
        
        return (fee, vendor_amount, succeed)


def request_payment(data=None):
    if not settings.LYSHOP_PAY_REQUEST_URL or not settings.PAY_USERNAME or not settings.PAY_REQUEST_TOKEN:
        logger.warning('PAY:USER or PAY_REQUEST_TOKEN environment variable is not defined.')
        return None
    url = settings.LYSHOP_PAY_REQUEST_URL
    headers={'Authorization': f"Token {settings.PAY_REQUEST_TOKEN}"}
    logger.debug(f'Sending payment request to url {url}')
    response = None
    try:
        response = requests.post(url, data=data, headers=headers)
        logger.debug(f'payment request response : {response}')
        if not response:
            logger.error(f"Error on requesting a payment to the url {url} : status code {response.status_code} - error : {response}")
    except Exception as e:
        logger.error(f"Error on sending Payment request at url {url}")
        logger.exception(e)
    return response


def process_vendor_payment(user):
    is_vendor = vendors_service.is_vendor(user)
    if not is_vendor:
        logger.warn("process_vendor_payment : user is not a vendor")
        return None
    
    vendor_balance = vendors_service.get_vendor_balance(user)
    policy_group = user.paymentpolicygroup_set.first()
    fee, vendor_amount, succeed = get_commission(vendor_balance.balance, policy_group.policy.commission)
    if not succeed:
        return None
    fee_user = None
    try:
        fee_user = User.objects.select_related('balance').get(username=settings.LYSHOP_FEE_USER)
    except ObjectDoesNotExist as e:
        logger.warn("process_vendor_payment : fee_user is missing")
        return False

    payment = None
    # From here with need to lock the DB
    with transaction.atomic():
        BalanceHistory.objects.create(balance=fee_user.balance, balance_ref_id=fee_user.balance.pk, current_amount=fee, balance_amount=fee_user.balance.balance, sender=user, receiver=fee_user)
        BalanceHistory.objects.create(balance=vendor_balance, balance_ref_id=vendor_balance.pk, current_amount=-vendor_balance.balance, balance_amount=vendor_balance.balance, sender=fee_user, receiver=user)
        Balance.objects.filter(user=fee_user).update(balance=F('balance') + fee)
        Balance.objects.filter(user=user).update(balance=0)
        payment = Payment.objects.create(monthly_limit=policy_group.policy.monthly_limit, commission=policy_group.policy.commission, policy=policy_group.policy, seller=user, amount=vendor_amount, balance_amount=vendor_balance.balance, pay_username=user.username)
    
    pay_request_data = {
        'sender' : settings.LYSHOP_USER,
        'recipient' : user.username,
        'amount' : vendor_amount,
    }
    #WIP

    return payment
