from django.test import TestCase
from lyshop import settings

# Create your tests here.


def test_get_payment_data():
    return {
                    'requester_name': settings.PAY_USERNAME,
                    'amount': 15000,

                    'customer_name': "LYSHOP TEST",
                    'quantity': 5,
                    'description': settings.PAY_REQUEST_DESCRIPTION,
                    'country' : "LYSHOP TEST COUNTRY",
                    'product_name' : 'LYSHOP TEST PRODUCT'
                }