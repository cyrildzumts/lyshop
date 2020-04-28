from lyshop import settings

import requests
import json
import logging
import uuid


logger = logging.getLogger(__name__)



def request_payment(url=None, **data):
    if not url or not data:
        return None
    
    if not settings.PAY_USERNAME or not settings.PAY_REQUEST_TOKEN:
        logger.warning('PAY:USER or PAY_REQUEST_TOKEN environment variable is not defined.')
        return None
    
    response = requests.post(url, data=data, auth=(settings.PAY_USERNAME, settings.PAY_REQUEST_TOKEN))
    
    if not response:
        logger.error(f"Error on requesting a payment to the url {url} : status code {response.status_code}")
        return None
    return response.json()['token']