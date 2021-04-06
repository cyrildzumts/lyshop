
from django.apps import apps
import secrets
import logging
import random

logger = logging.getLogger(__name__)
MAX_RECENTS = 3

PAGINATED_BY = 50
RAND_START = 0
RAND_END = 1000000

def get_postdata(request):
    return request.POST.copy()


def show_dict_contents(dict_obj, header):
    logger.info(f"Displaying Dict content for {header}")
    for k, v in dict_obj.items():
            logger.debug(f"key : \"{k}\" - value : \"{v}\"")
    logger.info(f"Displaying Dict content for {header} Done")

def get_session(request):
    return request.session

def get_data_from_request(request_dict, key):
    val = None
    if request_dict and key :
        val = request_dict[key]
    
    return val

    
def get_model(app_name=None, modelName=None):
    return apps.get_model(app_name, modelName)

def get_all_fields_from_form(instance):
    """"
    Return names of all available fields from given Form instance.

    :arg instance: Form instance
    :returns list of field names
    :return type: list
    """

    fields = list(instance().base_fields)

    for field in list(instance().declared_fields):
        if field not in fields:
            fields.append(field)
    return fields

def generate_token_10():
    return secrets.token_urlsafe(10)



def get_random_ref():
    return random.randrange(RAND_START, RAND_END)

def is_entry_key_in_tuples(key, tuples):
    found = False
    for k, v in tuples:
        if k == key:
            found = True
            break
    return found


def find_element_by_key_in_tuples(key, tuples):
    value = None
    for k, v in tuples:
        if k == key:
            value = v
            break
    return key, value

def find_element_by_value_in_tuples(value, tuples):
    key = None
    for k, v in tuples:
        if v == value:
            key = k
            break
    return key, value


def show_request(request):
    logger.info("REQUEST DATA")
    logger.info(f"SCHEME : {request.scheme}")
    logger.info(f"PATH : {request.path}")
    logger.info(f"PATH INFO: {request.path_info}")
    logger.info(f"METHOD : {request.method}")
    logger.info(f"ENCODING : {request.encoding}")
    logger.info(f"CONTENT_TYPE : {request.content_type}")
    logger.info(f"CONTENT_PARAMS : {request.content_params}")
    logger.info(f"GET : {request.GET}")
    logger.info("------------------------------")
    for k,v in request.GET.items():
        logger.info(f"{k} : {v}")
    logger.info("------------------------------")
    logger.info(f"POST : {request.POST}")
    logger.info("------------------------------")
    for k,v in request.POST.items():
        logger.info(f"{k} : {v}")
    logger.info("------------------------------")
    logger.info(f"COOKIES : {request.COOKIES}")
    logger.info(f"META : ")
    logger.info("------------------------------")
    for k,v in request.META.items():
        logger.info(f"{k} : {v}")
    logger.info("------------------------------")

    logger.info(f"HEADERS : ")
    for k,v in request.headers.items():
        logger.info(f"{k} : {v}")
    logger.info("------------------------------")
    logger.info("REQUEST CONTENT FINISHED")
